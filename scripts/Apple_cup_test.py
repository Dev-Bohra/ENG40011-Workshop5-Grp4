from ultralytics import YOLO
import cv2

# Load pretrained YOLOv8 nano model
model = YOLO("yolov8n.pt")

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Camera not detected")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Run detection
    results = model(frame, conf=0.7)

    # Draw detections
    annotated_frame = results[0].plot()

    # Show window
    cv2.imshow("Object Detection", annotated_frame)

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()