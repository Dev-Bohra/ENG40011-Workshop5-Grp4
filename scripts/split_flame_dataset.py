import random
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "flames"

CURRENT_TRAIN = DATASET / "train"
BACKUP = DATASET / "_original_train_backup"

random.seed(42)


def clear_folder(path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_split(files, source_labels, split_name):
    image_out = DATASET / split_name / "images"
    label_out = DATASET / split_name / "labels"

    clear_folder(image_out)
    clear_folder(label_out)

    for img in files:
        label = source_labels / f"{img.stem}.txt"

        shutil.copy2(img, image_out / img.name)

        if label.exists():
            shutil.copy2(label, label_out / label.name)


def main():
    # If backup does not exist, create it from current train folder
    if not BACKUP.exists():
        shutil.copytree(CURRENT_TRAIN, BACKUP)
        print("Backup created.")

    source_images = BACKUP / "images"
    source_labels = BACKUP / "labels"

    if not source_images.exists() or not source_labels.exists():
        print("Missing backup images or labels folder.")
        return

    images = list(source_images.glob("*.*"))
    random.shuffle(images)

    total = len(images)
    print(f"Found {total} images")

    train_end = int(total * 0.7)
    valid_end = int(total * 0.9)

    copy_split(images[:train_end], source_labels, "train")
    copy_split(images[train_end:valid_end], source_labels, "valid")
    copy_split(images[valid_end:], source_labels, "test")

    print("Done.")
    print(f"train: {train_end}")
    print(f"valid: {valid_end - train_end}")
    print(f"test: {total - valid_end}")


if __name__ == "__main__":
    main()