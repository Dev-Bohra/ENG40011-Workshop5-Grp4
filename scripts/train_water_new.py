from ultralytics import YOLO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATA_YAML = ROOT / "datasets" / "objects" / "water_bottle_new" / "data.yaml"
PROJECT_DIR = ROOT / "models" / "objects_exp3"


def train_water_bottle_exp2():
    model = YOLO("yolov8s.pt")  # slightly stronger than yolov8n

    model.train(
        data=str(DATA_YAML),
        epochs=75,
        imgsz=640,
        batch=8,
        project=str(PROJECT_DIR),
        name="water_bottle_new_yolov8s_75ep",
        patience=15,
        workers=0,
        device=0
    )


if __name__ == "__main__":
    train_water_bottle_exp2()