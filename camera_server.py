from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import time
from pathlib import Path
from datetime import date, datetime
from ultralytics import YOLO
from supabase import create_client

app = Flask(__name__)
CORS(app)

ROOT = Path(__file__).resolve().parent

OBJECT_MODEL_PATH = ROOT / "yolov8n.pt"
FIRE_MODEL_PATH = ROOT / "models" / "flame_exp1" / "flame_yolov8n_30ep" / "weights" / "best.pt"

EVIDENCE_DIR = ROOT / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)
'''
SUPABASE_URL = "Placeholder"
SUPABASE_KEY = "Placeholder"
SUPABASE_BUCKET = "task-evidence"
'''
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

object_model = YOLO(str(OBJECT_MODEL_PATH))
fire_model = YOLO(str(FIRE_MODEL_PATH))

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

last_fire_time = 0
fire_hold_seconds = 3

water_done = False
breakfast_done = False
last_sent_fire_alert = None

state = {"fire_alert": False}


def update_fire_alert_in_supabase(is_alert):
    global last_sent_fire_alert

    if last_sent_fire_alert == is_alert:
        return

    try:
        supabase.table("fire_alert_status").upsert({
            "id": 1,
            "fire_alert": is_alert,
            "message": "Fire detected" if is_alert else "No fire detected",
            "updated_at": datetime.now().isoformat()
        }).execute()

        last_sent_fire_alert = is_alert
        print(f"🔥 Fire alert updated in Supabase: {is_alert}")

    except Exception as e:
        print(f"❌ Failed to update fire alert in Supabase: {e}")


def upload_evidence_to_supabase(local_path, storage_filename):
    try:
        with open(local_path, "rb") as file:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                path=storage_filename,
                file=file,
                file_options={
                    "content-type": "image/jpeg",
                    "upsert": "true"
                }
            )

        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(
            storage_filename
        )

        print(f"📸 Uploaded evidence: {public_url}")
        return public_url

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None


def complete_task_in_supabase(keywords, evidence_url):
    today = date.today().isoformat()

    if isinstance(keywords, str):
        keywords = [keywords]

    try:
        all_tasks_result = supabase.table("care_tasks").select("*").execute()

        matched_task = None

        for task in all_tasks_result.data:
            content = str(task.get("content", "")).lower()

            for keyword in keywords:
                if keyword.lower() in content:
                    matched_task = task
                    break

            if matched_task:
                break

        if not matched_task:
            print(f"⚠️ No task found containing any of: {keywords}")
            print("Existing tasks:")
            for task in all_tasks_result.data:
                print("-", task.get("content"))
            return

        status_payload = {
            "task_id": matched_task["id"],
            "task_date": today,
            "status": "Completed",
            "evidence_url": evidence_url,
            "completed_by": "vision model",
            "completed_at": datetime.now().isoformat()
        }

        supabase.table("care_task_status").upsert(
            status_payload,
            on_conflict="task_id,task_date"
        ).execute()

        print(f"✅ Supabase updated: {matched_task['content']}")

    except Exception as e:
        print(f"❌ Supabase update failed for {keywords}: {e}")


def save_evidence_and_complete_task(keywords, frame, filename):
    image_path = EVIDENCE_DIR / filename

    cv2.imwrite(str(image_path), frame)

    timestamp = int(time.time())
    storage_filename = f"{timestamp}_{filename}"

    evidence_url = upload_evidence_to_supabase(
        image_path,
        storage_filename
    )

    if evidence_url:
        complete_task_in_supabase(
            keywords,
            evidence_url
        )


def draw_banner(frame, text, color):
    cv2.rectangle(frame, (10, 10), (780, 75), color, -1)
    cv2.putText(
        frame,
        text,
        (20, 52),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )


def generate_frames():
    global last_fire_time, water_done, breakfast_done

    while True:
        success, frame = camera.read()

        if not success:
            break

        fire_results = fire_model.predict(
            source=frame,
            conf=0.5,
            device=0,
            verbose=False
        )

        for box in fire_results[0].boxes:
            cls_id = int(box.cls[0])
            label = fire_model.names[cls_id].lower()

            if label == "fire":
                last_fire_time = time.time()
                break

        show_fire_prompt = (time.time() - last_fire_time) <= fire_hold_seconds
        state["fire_alert"] = show_fire_prompt
        update_fire_alert_in_supabase(show_fire_prompt)

        object_results = object_model.predict(
            source=frame,
            conf=0.45,
            verbose=False
        )

        annotated_frame = object_results[0].plot()

        labels = []

        for box in object_results[0].boxes:
            cls_id = int(box.cls[0])
            label = object_model.names[cls_id].lower()
            labels.append(label)

        has_bottle = "bottle" in labels
        has_cup = "cup" in labels
        has_apple = "apple" in labels

        if has_bottle and not water_done:
            save_evidence_and_complete_task(
                ["water", "drink"],
                annotated_frame,
                "water.jpg"
            )
            water_done = True

        if has_cup and has_apple and not breakfast_done:
            save_evidence_and_complete_task(
                ["breakfast", "meal", "food", "eat"],
                annotated_frame,
                "breakfast.jpg"
            )
            breakfast_done = True

        if show_fire_prompt:
            draw_banner(
                annotated_frame,
                "FIRE DETECTED - ALERT SENT TO CARETAKER",
                (0, 0, 255)
            )

        elif has_bottle:
            draw_banner(
                annotated_frame,
                "Bottle detected - Drink water task completed",
                (0, 150, 0)
            )

        elif has_cup and has_apple:
            draw_banner(
                annotated_frame,
                "Cup + apple detected - Breakfast task completed",
                (0, 150, 0)
            )

        ret, buffer = cv2.imencode(".jpg", annotated_frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/")
def index():
    return jsonify({
        "message": "Camera server running",
        "video": "/video",
        "alert_status": "/alert-status",
        "evidence": "Supabase Storage"
    })


@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/alert-status")
def alert_status():
    return jsonify({"fire_alert": state["fire_alert"]})


@app.route("/evidence/<filename>")
def evidence(filename):
    return send_from_directory(EVIDENCE_DIR, filename)


if __name__ == "__main__":
    print("Object model:", OBJECT_MODEL_PATH)
    print("Object model exists:", OBJECT_MODEL_PATH.exists())
    print("Fire model:", FIRE_MODEL_PATH)
    print("Fire model exists:", FIRE_MODEL_PATH.exists())
    print("Evidence folder:", EVIDENCE_DIR)
    print("Supabase bucket:", SUPABASE_BUCKET)

    if not camera.isOpened():
        print("❌ Camera not detected")
    else:
        print("✅ Camera detected")

    app.run(host="0.0.0.0", port=8080, debug=False)
