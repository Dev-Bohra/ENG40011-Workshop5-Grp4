import cv2
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

    while True:
        success, frame = cap.read()

        if not success:
            print("Failed to read webcam frame.")
            break

        results = model.predict(
            source=frame,
            conf=0.2,
            device=0,
            verbose=False
        )

        annotated_frame = results[0].plot()

        fire_detected = False

        for box in results[0].boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label == "fire" and conf >= 0.35:
                fire_detected = True

        if fire_detected:
            prompt = "FLAME DETECTED - Please check nearby hazards"
        else:
            prompt = "No flame detected"

        cv2.putText(
            annotated_frame,
            prompt,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255) if fire_detected else (0, 255, 0),
            2
        )

        cv2.imshow("Flame Detection - Press Q to Quit", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()