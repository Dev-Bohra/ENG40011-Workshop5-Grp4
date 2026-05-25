import cv2
from ultralytics import YOLO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    ROOT
    / "models"
    / "objects_exp2"
    / "water_bottle_yolov8s_75ep"
    / "weights"
    / "best.pt"
)


def main():
    print("Loading model...")
    model = YOLO(str(MODEL_PATH))

    print("Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        success, frame = cap.read()

        if not success:
            print("Failed to grab frame.")
            break

        # Run YOLO inference
        results = model.predict(
            source=frame,
            conf=0.5,
            verbose=False
        )

        # Draw bounding boxes
        annotated_frame = results[0].plot()

        # Show webcam
        cv2.imshow(
            "Water Bottle Detection - Press Q to Quit",
            annotated_frame
        )

        # Quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()