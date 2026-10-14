from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
# ==============================
# PROJECT PATHS
# ==============================
PROJECT_ROOT = Path(__file__).resolve().parent
IMAGE_DIR = PROJECT_ROOT / "data" / "processed" / "images"
LABEL_DIR = PROJECT_ROOT / "data" / "processed" / "labels"
OUTPUT_FILE = PROJECT_ROOT / "annotation_check.jpg"

# ==============================
# SETTINGS
# ==============================
THUMBNAIL_WIDTH = 300
THUMBNAIL_HEIGHT = 300
COLUMNS = 4
CLASS_NAMES = {
   0: "multimeter",
   1: "display"
}

# ==============================
# LOAD IMAGES
# ==============================
image_files = sorted([
   p for p in IMAGE_DIR.iterdir()
   if p.suffix.lower() in {
       ".jpg", ".jpeg", ".png", ".bmp", ".webp"
   }
])
print(f"Found {len(image_files)} images.")

# ==============================
# CREATE THUMBNAILS
# ==============================
thumbnails = []
for image_path in image_files:
   try:
       image = Image.open(image_path).convert("RGB")
       original_width, original_height = image.size
       # Resize while preserving aspect ratio
       image.thumbnail(
           (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
       )
       display_width, display_height = image.size
       draw = ImageDraw.Draw(image)
       # Corresponding YOLO label
       label_path = LABEL_DIR / f"{image_path.stem}.txt"
       if label_path.exists():
           lines = label_path.read_text().strip().splitlines()
           for line in lines:
               parts = line.split()
               if len(parts) != 5:
                   continue
               class_id = int(parts[0])
               x_center = float(parts[1])
               y_center = float(parts[2])
               width = float(parts[3])
               height = float(parts[4])
               # YOLO normalized → original pixels
               x_center *= original_width
               y_center *= original_height
               width *= original_width
               height *= original_height
               x1 = x_center - width / 2
               y1 = y_center - height / 2
               x2 = x_center + width / 2
               y2 = y_center + height / 2
               # Original pixels → thumbnail pixels
               scale_x = display_width / original_width
               scale_y = display_height / original_height
               x1 *= scale_x
               x2 *= scale_x
               y1 *= scale_y
               y2 *= scale_y
               # Different outline for different classes
               if class_id == 0:
                   outline = "blue"
               else:
                   outline = "red"
               draw.rectangle(
                   [x1, y1, x2, y2],
                   outline=outline,
                   width=3
               )
               label = CLASS_NAMES.get(
                   class_id,
                   f"class_{class_id}"
               )
               draw.text(
                   (x1 + 3, max(0, y1 - 15)),
                   label,
                   fill=outline
               )
       # Add filename
       draw.text(
           (5, 5),
           image_path.name[:35],
           fill="white",
           stroke_width=2,
           stroke_fill="black"
       )
       thumbnails.append(image)
   except Exception as e:
       print(f"ERROR: {image_path.name}: {e}")

# ==============================
# CREATE CONTACT SHEET
# ==============================
if not thumbnails:
   print("No images found.")
   raise SystemExit

rows = (len(thumbnails) + COLUMNS - 1) // COLUMNS
sheet_width = COLUMNS * THUMBNAIL_WIDTH
sheet_height = rows * THUMBNAIL_HEIGHT
sheet = Image.new(
   "RGB",
   (sheet_width, sheet_height),
   "black"
)

# ==============================
# PLACE THUMBNAILS
# ==============================
for index, thumbnail in enumerate(thumbnails):
   row = index // COLUMNS
   column = index % COLUMNS
   x = column * THUMBNAIL_WIDTH
   y = row * THUMBNAIL_HEIGHT
   sheet.paste(thumbnail, (x, y))

# ==============================
# SAVE
# ==============================
sheet.save(OUTPUT_FILE, quality=95)
print("\n================================")
print("ANNOTATION CHECK CREATED")
print("================================")
print(f"Output: {OUTPUT_FILE}")
print(f"Images checked: {len(thumbnails)}")