from pathlib import Path
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]

DATA_YAML = ROOT / "datasets" / "flames" / "data.yaml"
PROJECT_DIR = ROOT / "models" / "flame_exp1"


def train_flame_detector():
    model = YOLO("yolov8n.pt")

    model.train(
        data=str(DATA_YAML),
        epochs=30,
        imgsz=640,
        batch=16,
        project=str(PROJECT_DIR),
        name="flame_yolov8n_30ep",
        patience=8,
        workers=0,
        device=0
    )


if __name__ == "__main__":
    train_flame_detector()