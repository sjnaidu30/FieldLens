from pathlib import Path
LABEL_DIR = Path("data/processed/labels")
for label_file in sorted(LABEL_DIR.glob("*.txt")):
   counts = {
       0: 0,  # multimeter
       1: 0   # display
   }
   with open(label_file, "r") as f:
       for line in f:
           parts = line.strip().split()
           if not parts:
               continue
           class_id = int(parts[0])
           if class_id in counts:
               counts[class_id] += 1
   if counts[0] != 1 or counts[1] != 1:
       print(
           f"{label_file.name}: "
           f"multimeter={counts[0]}, display={counts[1]}"
       )