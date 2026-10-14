from pathlib import Path
from PIL import Image
import math
PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_DIR = PROJECT_ROOT / "dataset"
SPLITS = ("train", "val")
VALID_CLASSES = {0, 1}
CLASS_NAMES = {0: "multimeter", 1: "display"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def get_images(directory: Path) -> dict[str, Path]:
   return {
       p.stem: p
       for p in directory.iterdir()
       if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
   }

def get_labels(directory: Path) -> dict[str, Path]:
   return {
       p.stem: p
       for p in directory.glob("*.txt")
       if p.is_file()
   }

def main() -> None:
   errors = []
   totals = {
       "images": 0,
       "labels": 0,
       "missing": 0,
       "orphan": 0,
       "corrupt": 0,
       "empty": 0,
       "invalid": 0,
   }
   class_counts = {0: 0, 1: 0}
   for split in SPLITS:
       image_dir = DATASET_DIR / "images" / split
       label_dir = DATASET_DIR / "labels" / split
       print(f"\n========== {split.upper()} ==========")
       if not image_dir.is_dir() or not label_dir.is_dir():
           message = f"Missing directory: {image_dir} or {label_dir}"
           print(f"ERROR: {message}")
           errors.append(message)
           continue
       images = get_images(image_dir)
       labels = get_labels(label_dir)
       missing = sorted(images.keys() - labels.keys())
       orphan = sorted(labels.keys() - images.keys())
       totals["images"] += len(images)
       totals["labels"] += len(labels)
       totals["missing"] += len(missing)
       totals["orphan"] += len(orphan)
       print(f"Images: {len(images)}")
       print(f"Labels: {len(labels)}")
       for name in missing:
           errors.append(f"{split}: image missing label: {name}")
       for name in orphan:
           errors.append(f"{split}: label missing image: {name}")
       if not missing and not orphan:
           print("Image-label pairing: OK")
       for image_path in images.values():
           try:
               with Image.open(image_path) as img:
                   img.verify()
           except Exception as exc:
               totals["corrupt"] += 1
               errors.append(
                   f"{split}: unreadable image {image_path.name}: {exc}"
               )
       for name, label_path in labels.items():
           try:
               content = label_path.read_text(encoding="utf-8").strip()
           except Exception as exc:
               totals["invalid"] += 1
               errors.append(f"{split}: cannot read {label_path.name}: {exc}")
               continue
           if not content:
               totals["empty"] += 1
               errors.append(f"{split}: empty label file: {label_path.name}")
               continue
           for line_no, line in enumerate(content.splitlines(), start=1):
               parts = line.split()
               prefix = f"{split}: {label_path.name}, line {line_no}"
               if len(parts) != 5:
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: expected 5 values, got {len(parts)}")
                   continue
               try:
                   class_id = int(parts[0])
                   x, y, width, height = map(float, parts[1:])
               except ValueError:
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: non-numeric or invalid class ID")
                   continue
               if class_id not in VALID_CLASSES:
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: invalid class ID {class_id}")
                   continue
               if not all(math.isfinite(v) for v in (x, y, width, height)):
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: coordinates must be finite numbers")
                   continue
               if not all(0 <= v <= 1 for v in (x, y, width, height)):
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: coordinates outside [0, 1]")
                   continue
               if width <= 0 or height <= 0:
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: width and height must be positive")
                   continue
               # Check that the bounding box remains inside the image.
               if (
                   x - width / 2 < 0
                   or y - height / 2 < 0
                   or x + width / 2 > 1
                   or y + height / 2 > 1
               ):
                   totals["invalid"] += 1
                   errors.append(f"{prefix}: bounding box extends outside image")
                   continue
               class_counts[class_id] += 1
   print("\n========== SUMMARY ==========")
   for key, value in totals.items():
       print(f"{key.capitalize():12}: {value}")
   print("\nObject counts:")
   for class_id, count in class_counts.items():
       print(f"{class_id} = {CLASS_NAMES[class_id]}: {count}")
   if errors:
       print(f"\nDATASET NEEDS ATTENTION ({len(errors)} issues)")
       for error in errors:
           print(f"- {error}")
       raise SystemExit(1)
   print("\nDATASET PASSED STRUCTURAL VALIDATION")

if __name__ == "__main__":
   main()