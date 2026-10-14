from pathlib import Path
import random
import shutil
# Source folders
IMAGE_DIR = Path("data/processed/images")
LABEL_DIR = Path("data/processed/labels")
# Destination folders
TRAIN_IMAGES = Path("dataset/images/train")
VAL_IMAGES = Path("dataset/images/val")
TRAIN_LABELS = Path("dataset/labels/train")
VAL_LABELS = Path("dataset/labels/val")
# Create folders
for folder in [TRAIN_IMAGES, VAL_IMAGES, TRAIN_LABELS, VAL_LABELS]:
   folder.mkdir(parents=True, exist_ok=True)
# Find images
images = []
for ext in ["*.jpg", "*.jpeg", "*.png"]:
   images.extend(IMAGE_DIR.glob(ext))
# Sort for reproducibility
images = sorted(images)
print(f"Found {len(images)} images.")
# Shuffle randomly
random.seed(42)
random.shuffle(images)
# 80% train, 20% validation
split_index = int(len(images) * 0.8)
train_images = images[:split_index]
val_images = images[split_index:]
print(f"Training images:   {len(train_images)}")
print(f"Validation images: {len(val_images)}")

def copy_dataset(image_list, image_destination, label_destination):
   for image_path in image_list:
       # Matching label has the same filename stem
       label_path = LABEL_DIR / f"{image_path.stem}.txt"
       if not label_path.exists():
           print(f"WARNING: Missing label for {image_path.name}")
           continue
       # Copy image
       shutil.copy2(
           image_path,
           image_destination / image_path.name
       )
       # Copy matching YOLO label
       shutil.copy2(
           label_path,
           label_destination / label_path.name
       )

# Copy training data
copy_dataset(
   train_images,
   TRAIN_IMAGES,
   TRAIN_LABELS
)
# Copy validation data
copy_dataset(
   val_images,
   VAL_IMAGES,
   VAL_LABELS
)
print()
print("Dataset split completed!")