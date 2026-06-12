import cv2
import time
from pathlib import Path
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    ROOT
    / "models"
    / "flame_exp1"
    / "flame_yolov8n_30ep"
    / "weights"
    / "best.pt"
)


def main():
    print("Model path:", MODEL_PATH)
    print("Exists:", MODEL_PATH.exists())

    model = YOLO(str(MODEL_PATH))

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    last_fire_time = 0
    fire_hold_seconds = 3

    while True:
        success, frame = cap.read()

        if not success:
            print("Failed to read webcam frame.")
            break

        results = model.predict(
            source=frame,
            conf=0.5,
            device=0,
            verbose=False
        )

        annotated_frame = results[0].plot()

        fire_detected_now = False

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id].lower()

            if label == "fire":
                fire_detected_now = True
                last_fire_time = time.time()
                break

        show_fire_prompt = (time.time() - last_fire_time) <= fire_hold_seconds

        if show_fire_prompt:
            prompt = "FLAME DETECTED - Please take action"

            # Draw solid background so text is not hidden by YOLO boxes
            cv2.rectangle(
                annotated_frame,
                (10, 10),
                (620, 60),
                (0, 0, 255),
                -1
            )

            cv2.putText(
                annotated_frame,
                prompt,
                (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        cv2.imshow("Flame Detection - Press Q to Quit", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()