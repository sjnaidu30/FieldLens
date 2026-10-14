import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
import shutil

# ============================================================
# PATHS
# ============================================================
BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw" / "images"
PROCESSED = BASE / "data" / "processed"
OUT_IMAGES = PROCESSED / "images"
OUT_LABELS = PROCESSED / "labels"
OUT_IMAGES.mkdir(parents=True, exist_ok=True)
OUT_LABELS.mkdir(parents=True, exist_ok=True)

# ============================================================
# CLASSES
# ============================================================
CLASSES = {
   "multimeter": 0,
   "display": 1
}
ID_TO_CLASS = {
   0: "multimeter",
   1: "display"
}

# ============================================================
# IMAGE FORMATS
# ============================================================
EXTENSIONS = {
   ".jpg",
   ".jpeg",
   ".png",
   ".bmp",
   ".webp"
}

# ============================================================
# ANNOTATOR
# ============================================================
class Annotator:
   def __init__(self, root):
       self.root = root
       self.root.title(
           "Multimeter Annotation Tool"
       )
       self.root.geometry(
           "1500x950"
       )
       # ----------------------------------------------------
       # FIND IMAGES
       # ----------------------------------------------------
       self.files = []
       for folder in ["good", "bad"]:
           folder_path = RAW / folder
           if not folder_path.exists():
               continue
           for file in folder_path.iterdir():
               if file.suffix.lower() in EXTENSIONS:
                   self.files.append(file)
       self.files.sort(
           key=lambda p: (
               p.parent.name.lower(),
               p.name.lower()
           )
       )
       self.index = 0
       # ----------------------------------------------------
       # IMAGE
       # ----------------------------------------------------
       self.image = None
       self.photo = None
       self.original_width = 0
       self.original_height = 0
       # Zoom
       self.zoom = 1.0
       self.min_zoom = 0.2
       self.max_zoom = 5.0
       # Image displayed position
       self.offset_x = 0
       self.offset_y = 0
       # ----------------------------------------------------
       # ANNOTATIONS
       # ----------------------------------------------------
       self.boxes = []
       self.selected = None
       # ----------------------------------------------------
       # MOUSE
       # ----------------------------------------------------
       self.mode = None
       self.handle = None
       self.start_x = 0
       self.start_y = 0
       self.last_x = 0
       self.last_y = 0
       # ----------------------------------------------------
       # UNSAVED CHANGES
       # ----------------------------------------------------
       self.dirty = False
       # ----------------------------------------------------
       # BUILD UI
       # ----------------------------------------------------
       self.create_ui()
       if self.files:
           self.load_image(0)
       else:
           self.status.set(
               "No images found in data/raw/images/good or bad"
           )

   # ========================================================
   # UI
   # ========================================================
   def create_ui(self):
       # ----------------------------------------------------
       # TOP BAR
       # ----------------------------------------------------
       top = tk.Frame(
           self.root,
           bg="#222222"
       )
       top.pack(
           fill=tk.X
       )

       tk.Label(
           top,
           text="MULTIMETER ANNOTATOR",
           bg="#222222",
           fg="white",
           font=("Arial", 16, "bold")
       ).pack(
           side=tk.LEFT,
           padx=15,
           pady=10
       )

       # Class
       tk.Label(
           top,
           text="Class:",
           bg="#222222",
           fg="white"
       ).pack(
           side=tk.LEFT
       )

       self.class_var = tk.StringVar(
           value="multimeter"
       )

       tk.OptionMenu(
           top,
           self.class_var,
           "multimeter",
           "display"
       ).pack(
           side=tk.LEFT,
           padx=5
       )

       # Previous
       tk.Button(
           top,
           text="← Previous",
           command=self.previous
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Next
       tk.Button(
           top,
           text="Next →",
           command=self.next
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Save
       tk.Button(
           top,
           text="SAVE",
           bg="#1976D2",
           fg="white",
           command=self.save
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Save & Next
       tk.Button(
           top,
           text="SAVE & NEXT",
           bg="#2E7D32",
           fg="white",
           command=self.save_next
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Delete
       tk.Button(
           top,
           text="Delete Box",
           command=self.delete_box
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Clear
       tk.Button(
           top,
           text="Clear",
           command=self.clear
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Zoom out
       tk.Button(
           top,
           text="−",
           width=3,
           command=lambda: self.change_zoom(
               0.8
           )
       ).pack(
           side=tk.LEFT,
           padx=(15, 2)
       )

       # Zoom label
       self.zoom_text = tk.StringVar(
           value="100%"
       )

       tk.Label(
           top,
           textvariable=self.zoom_text,
           bg="#222222",
           fg="white",
           width=6
       ).pack(
           side=tk.LEFT
       )

       # Zoom in
       tk.Button(
           top,
           text="+",
           width=3,
           command=lambda: self.change_zoom(
               1.25
           )
       ).pack(
           side=tk.LEFT,
           padx=2
       )

       # Fit
       tk.Button(
           top,
           text="FIT",
           command=self.fit_to_window
       ).pack(
           side=tk.LEFT,
           padx=4
       )

       # Progress
       self.progress = tk.StringVar()
       tk.Label(
           top,
           textvariable=self.progress,
           bg="#222222",
           fg="white"
       ).pack(
           side=tk.RIGHT,
           padx=15
       )

       # ----------------------------------------------------
       # MAIN
       # ----------------------------------------------------
       main = tk.Frame(
           self.root,
           bg="#111111"
       )
       main.pack(
           fill=tk.BOTH,
           expand=True
       )

       # ----------------------------------------------------
       # IMAGE LIST
       # ----------------------------------------------------
       left = tk.Frame(
           main,
           bg="#1E1E1E",
           width=280
       )
       left.pack(
           side=tk.LEFT,
           fill=tk.Y
       )

       self.listbox = tk.Listbox(
           left,
           width=38,
           bg="#252525",
           fg="white",
           selectbackground="#1976D2"
       )
       self.listbox.pack(
           fill=tk.BOTH,
           expand=True,
           padx=8,
           pady=8
       )

       for file in self.files:
           self.listbox.insert(
               tk.END,
               f"[{file.parent.name}] {file.name}"
           )

       self.listbox.bind(
           "<<ListboxSelect>>",
           self.list_select
       )

       # ----------------------------------------------------
       # CANVAS
       # ----------------------------------------------------
       canvas_frame = tk.Frame(
           main,
           bg="#111111"
       )
       canvas_frame.pack(
           side=tk.LEFT,
           fill=tk.BOTH,
           expand=True
       )

       self.canvas = tk.Canvas(
           canvas_frame,
           bg="#111111",
           highlightthickness=0
       )
       self.canvas.pack(
           fill=tk.BOTH,
           expand=True
       )

       # Mouse
       self.canvas.bind(
           "<ButtonPress-1>",
           self.mouse_down
       )
       self.canvas.bind(
           "<B1-Motion>",
           self.mouse_move
       )
       self.canvas.bind(
           "<ButtonRelease-1>",
           self.mouse_up
       )

       # Mouse wheel
       self.canvas.bind(
           "<MouseWheel>",
           self.mouse_wheel
       )
       # Linux mouse wheel
       self.canvas.bind(
           "<Button-4>",
           lambda e: self.change_zoom(1.15)
       )
       self.canvas.bind(
           "<Button-5>",
           lambda e: self.change_zoom(0.87)
       )

       # ----------------------------------------------------
       # STATUS
       # ----------------------------------------------------
       self.status = tk.StringVar(
           value="Ready"
       )

       tk.Label(
           self.root,
           textvariable=self.status,
           bg="#222222",
           fg="#CCCCCC",
           anchor="w"
       ).pack(
           fill=tk.X
       )

       # Keyboard
       self.root.bind(
           "<Delete>",
           lambda e: self.delete_box()
       )
       self.root.bind(
           "<Escape>",
           lambda e: self.cancel()
       )

   # ========================================================
   # LOAD IMAGE
   # ========================================================
   def load_image(self, index):
       if not self.files:
           return

       self.index = max(
           0,
           min(
               index,
               len(self.files) - 1
           )
       )

       path = self.files[
           self.index
       ]

       try:
           self.image = Image.open(
               path
           ).convert("RGB")
       except Exception as e:
           messagebox.showerror(
               "Image Error",
               str(e)
           )
           return

       self.original_width = self.image.width
       self.original_height = self.image.height

       self.load_labels()

       self.dirty = False

       self.root.update_idletasks()

       self.fit_to_window()

       self.listbox.selection_clear(
           0,
           tk.END
       )
       self.listbox.selection_set(
           self.index
       )
       self.listbox.see(
           self.index
       )

       self.update_progress()

       self.status.set(
           f"Loaded: {path.parent.name}/{path.name}"
       )

   # ========================================================
   # FIT TO WINDOW
   # ========================================================
   def fit_to_window(self):
       if self.image is None:
           return

       cw = max(
           100,
           self.canvas.winfo_width() - 30
       )
       ch = max(
           100,
           self.canvas.winfo_height() - 30
       )

       iw = self.image.width
       ih = self.image.height

       self.zoom = min(
           cw / iw,
           ch / ih
       )

       self.zoom = max(
           self.min_zoom,
           min(
               self.zoom,
               self.max_zoom
           )
       )

       self.update_image()

   # ========================================================
   # CHANGE ZOOM
   # ========================================================
   def change_zoom(
       self,
       factor
   ):
       if self.image is None:
           return

       new_zoom = (
           self.zoom * factor
       )

       new_zoom = max(
           self.min_zoom,
           min(
               new_zoom,
               self.max_zoom
           )
       )

       if new_zoom == self.zoom:
           return

       self.zoom = new_zoom

       self.update_image()

   # ========================================================
   # MOUSE WHEEL ZOOM
   # ========================================================
   def mouse_wheel(self, event):
       if event.delta > 0:
           self.change_zoom(1.15)
       else:
           self.change_zoom(0.87)

   # ========================================================
   # UPDATE IMAGE
   # ========================================================
   def update_image(self):
       if self.image is None:
           return

       w = max(
           1,
           int(
               self.image.width *
               self.zoom
           )
       )
       h = max(
           1,
           int(
               self.image.height *
               self.zoom
           )
       )

       resized = self.image.resize(
           (w, h),
           Image.Resampling.LANCZOS
       )

       self.photo = ImageTk.PhotoImage(
           resized
       )

       self.canvas.delete(
           "all"
       )

       cw = self.canvas.winfo_width()
       ch = self.canvas.winfo_height()

       self.offset_x = (
           cw - w
       ) // 2
       self.offset_y = (
           ch - h
       ) // 2

       self.canvas.create_image(
           self.offset_x,
           self.offset_y,
           anchor="nw",
           image=self.photo
       )

       self.zoom_text.set(
           f"{int(self.zoom * 100)}%"
       )

       self.draw_boxes()

   # ========================================================
   # DRAW BOXES
   # ========================================================
   def draw_boxes(self):
       for i, box in enumerate(
           self.boxes
       ):
           self.draw_box(
               i,
               box
           )

   # ========================================================
   # DRAW BOX
   # ========================================================
   def draw_box(
       self,
       i,
       box
   ):
       x1 = (
           self.offset_x +
           box["x1"] * self.zoom
       )
       y1 = (
           self.offset_y +
           box["y1"] * self.zoom
       )
       x2 = (
           self.offset_x +
           box["x2"] * self.zoom
       )
       y2 = (
           self.offset_y +
           box["y2"] * self.zoom
       )

       if box["class"] == 0:
           color = "#00A8FF"
       else:
           color = "#FF4040"

       width = (
           4
           if i == self.selected
           else 2
       )

       self.canvas.create_rectangle(
           x1,
           y1,
           x2,
           y2,
           outline=color,
           width=width
       )

       self.canvas.create_text(
           x1 + 6,
           y1 + 6,
           anchor="nw",
           text=box["label"],
           fill=color,
           font=("Arial", 12, "bold")
       )

       # Resize handles
       if i == self.selected:
           for _, hx, hy in self.handles(box):
               size = 7
               self.canvas.create_rectangle(
                   hx - size,
                   hy - size,
                   hx + size,
                   hy + size,
                   fill="white",
                   outline="black"
               )

   # ========================================================
   # HANDLES
   # ========================================================
   def handles(self, box):
       x1 = (
           self.offset_x +
           box["x1"] * self.zoom
       )
       y1 = (
           self.offset_y +
           box["y1"] * self.zoom
       )
       x2 = (
           self.offset_x +
           box["x2"] * self.zoom
       )
       y2 = (
           self.offset_y +
           box["y2"] * self.zoom
       )

       xm = (
           x1 + x2
       ) / 2
       ym = (
           y1 + y2
       ) / 2

       return [
           ("nw", x1, y1),
           ("n", xm, y1),
           ("ne", x2, y1),
           ("w", x1, ym),
           ("e", x2, ym),
           ("sw", x1, y2),
           ("s", xm, y2),
           ("se", x2, y2)
       ]

   # ========================================================
   # FIND BOX
   # ========================================================
   def find_box(
       self,
       x,
       y
   ):
       for i in range(
           len(self.boxes) - 1,
           -1,
           -1
       ):
           b = self.boxes[i]

           x1 = min(
               b["x1"],
               b["x2"]
           )
           x2 = max(
               b["x1"],
               b["x2"]
           )
           y1 = min(
               b["y1"],
               b["y2"]
           )
           y2 = max(
               b["y1"],
               b["y2"]
           )

           if (
               x1 <= x <= x2
               and
               y1 <= y <= y2
           ):
               return i

       return None

   # ========================================================
   # FIND HANDLE
   # ========================================================
   def find_handle(
       self,
       x,
       y,
       box
   ):
       for name, hx, hy in self.handles(box):
           if (
               abs(x - hx) <= 12
               and
               abs(y - hy) <= 12
           ):
               return name

       return None

   # ========================================================
   # MOUSE DOWN
   # ========================================================
   def mouse_down(
       self,
       event
   ):
       if self.image is None:
           return

       ix = (
           event.x -
           self.offset_x
       ) / self.zoom
       iy = (
           event.y -
           self.offset_y
       ) / self.zoom

       # ----------------------------------------------------
       # Ignore clicks outside image
       # ----------------------------------------------------
       if (
           ix < 0
           or
           iy < 0
           or
           ix > self.image.width
           or
           iy > self.image.height
       ):
           return

       # ----------------------------------------------------
       # RESIZE
       # ----------------------------------------------------
       if self.selected is not None:
           handle = self.find_handle(
               event.x,
               event.y,
               self.boxes[
                   self.selected
               ]
           )

           if handle:
               self.mode = "resize"
               self.handle = handle
               self.dirty = True
               return

       # ----------------------------------------------------
       # MOVE
       # ----------------------------------------------------
       found = self.find_box(
           ix,
           iy
       )

       if found is not None:
           self.selected = found
           self.mode = "move"
           self.last_x = ix
           self.last_y = iy
           self.dirty = True
           self.draw_boxes()
           return

       # ----------------------------------------------------
       # NEW BOX
       # ----------------------------------------------------
       class_name = (
           self.class_var.get()
       )

       class_id = CLASSES[
           class_name
       ]

       self.boxes.append({
           "class":
               class_id,
           "label":
               class_name,
           "x1":
               ix,
           "y1":
               iy,
           "x2":
               ix,
           "y2":
               iy
       })

       self.selected = (
           len(self.boxes) - 1
       )

       self.mode = "draw"
       self.start_x = ix
       self.start_y = iy
       self.dirty = True

   # ========================================================
   # MOUSE MOVE
   # ========================================================
   def mouse_move(
       self,
       event
   ):
       if (
           self.mode is None
           or
           self.selected is None
       ):
           return

       ix = (
           event.x -
           self.offset_x
       ) / self.zoom
       iy = (
           event.y -
           self.offset_y
       ) / self.zoom

       ix = max(
           0,
           min(
               ix,
               self.image.width
           )
       )

       iy = max(
           0,
           min(
               iy,
               self.image.height
           )
       )

       box = self.boxes[
           self.selected
       ]

       # ----------------------------------------------------
       # DRAW
       # ----------------------------------------------------
       if self.mode == "draw":
           box["x1"] = min(
               self.start_x,
               ix
           )
           box["y1"] = min(
               self.start_y,
               iy
           )
           box["x2"] = max(
               self.start_x,
               ix
           )
           box["y2"] = max(
               self.start_y,
               iy
           )

       # ----------------------------------------------------
       # MOVE
       # ----------------------------------------------------
       elif self.mode == "move":
           dx = ix - self.last_x
           dy = iy - self.last_y

           width = (
               box["x2"] -
               box["x1"]
           )
           height = (
               box["y2"] -
               box["y1"]
           )

           nx = max(
               0,
               min(
                   box["x1"] + dx,
                   self.image.width - width
               )
           )

           ny = max(
               0,
               min(
                   box["y1"] + dy,
                   self.image.height - height
               )
           )

           box["x1"] = nx
           box["y1"] = ny
           box["x2"] = nx + width
           box["y2"] = ny + height

           self.last_x = ix
           self.last_y = iy

       # ----------------------------------------------------
       # RESIZE
       # ----------------------------------------------------
       elif self.mode == "resize":
           self.resize_box(
               box,
               ix,
               iy
           )

       self.update_image()

   # ========================================================
   # RESIZE BOX
   # ========================================================
   def resize_box(
       self,
       b,
       x,
       y
   ):
       w = self.image.width
       h = self.image.height

       if self.handle in (
           "nw",
           "w",
           "sw"
       ):
           b["x1"] = max(
               0,
               min(
                   x,
                   b["x2"] - 5
               )
           )

       if self.handle in (
           "ne",
           "e",
           "se"
       ):
           b["x2"] = min(
               w,
               max(
                   x,
                   b["x1"] + 5
               )
           )

       if self.handle in (
           "nw",
           "n",
           "ne"
       ):
           b["y1"] = max(
               0,
               min(
                   y,
                   b["y2"] - 5
               )
           )

       if self.handle in (
           "sw",
           "s",
           "se"
       ):
           b["y2"] = min(
               h,
               max(
                   y,
                   b["y1"] + 5
               )
           )

   # ========================================================
   # MOUSE UP
   # ========================================================
   def mouse_up(
       self,
       event
   ):
       self.mode = None
       self.handle = None

       if self.selected is not None:
           b = self.boxes[
               self.selected
           ]

           if (
               b["x2"] - b["x1"] < 5
               or
               b["y2"] - b["y1"] < 5
           ):
               self.boxes.pop(
                   self.selected
               )
               self.selected = None

       self.update_image()

   # ========================================================
   # DELETE BOX
   # ========================================================
   def delete_box(self):
       if self.selected is None:
           return

       self.boxes.pop(
           self.selected
       )

       self.selected = None
       self.dirty = True
       self.update_image()

   # ========================================================
   # CLEAR
   # ========================================================
   def clear(self):
       if not self.boxes:
           return

       answer = messagebox.askyesno(
           "Clear",
           "Delete all boxes on this image?"
       )

       if not answer:
           return

       self.boxes = []
       self.selected = None
       self.dirty = True
       self.update_image()

   # ========================================================
   # SAVE
   # ========================================================
   def save(self):
       if self.image is None:
           return False

       image_path = self.files[
           self.index
       ]

       label_path = (
           OUT_LABELS /
           f"{image_path.stem}.txt"
       )

       # ----------------------------------------------------
       # EMPTY ANNOTATION
       # ----------------------------------------------------
       if not self.boxes:
           if label_path.exists():
               label_path.unlink()

           self.status.set(
               "⚠ No boxes — image NOT saved"
           )
           self.dirty = False
           self.update_progress()
           return False

       # ----------------------------------------------------
       # COPY IMAGE
       # ----------------------------------------------------
       destination_image = (
           OUT_IMAGES /
           image_path.name
       )

       shutil.copy2(
           image_path,
           destination_image
       )

       # ----------------------------------------------------
       # YOLO
       # ----------------------------------------------------
       iw = self.image.width
       ih = self.image.height

       lines = []

       for b in self.boxes:
           x1 = min(
               b["x1"],
               b["x2"]
           )
           y1 = min(
               b["y1"],
               b["y2"]
           )
           x2 = max(
               b["x1"],
               b["x2"]
           )
           y2 = max(
               b["y1"],
               b["y2"]
           )

           width = x2 - x1
           height = y2 - y1

           cx = (
               (x1 + x2) / 2
           ) / iw
           cy = (
               (y1 + y2) / 2
           ) / ih

           nw = width / iw
           nh = height / ih

           lines.append(
               f"{b['class']} "
               f"{cx:.6f} "
               f"{cy:.6f} "
               f"{nw:.6f} "
               f"{nh:.6f}"
           )

       label_path.write_text(
           "\n".join(lines),
           encoding="utf-8"
       )

       self.dirty = False

       self.status.set(
           f"✓ SAVED: {image_path.name}"
       )

       self.update_progress()
       return True

   # ========================================================
   # SAVE & NEXT
   # ========================================================
   def save_next(self):
       success = self.save()

       if not success:
           return

       if self.index < len(self.files) - 1:
           self.load_image(
               self.index + 1
           )
       else:
           self.status.set(
               "✓ All images completed"
           )

   # ========================================================
   # SAFE NAVIGATION
   # ========================================================
   def can_leave(self):
       if not self.dirty:
           return True

       answer = messagebox.askyesnocancel(
           "Unsaved Annotation",
           "This image has unsaved changes.\n\n"
           "Yes = Save\n"
           "No = Discard\n"
           "Cancel = Stay"
       )

       if answer is None:
           return False

       if answer:
           return self.save()

       self.dirty = False
       return True

   # ========================================================
   # NEXT
   # ========================================================
   def next(self):
       if self.index >= len(self.files) - 1:
           return

       if not self.can_leave():
           return

       self.load_image(
           self.index + 1
       )

   # ========================================================
   # PREVIOUS
   # ========================================================
   def previous(self):
       if self.index <= 0:
           return

       if not self.can_leave():
           return

       self.load_image(
           self.index - 1
       )

   # ========================================================
   # LOAD EXISTING LABEL
   # ========================================================
   def load_labels(self):
       self.boxes = []
       self.selected = None

       image_path = self.files[
           self.index
       ]

       label_path = (
           OUT_LABELS /
           f"{image_path.stem}.txt"
       )

       if not label_path.exists():
           return

       iw = self.image.width
       ih = self.image.height

       try:
           lines = label_path.read_text(
               encoding="utf-8"
           ).splitlines()
       except Exception:
           return

       for line in lines:
           parts = line.split()

           if len(parts) != 5:
               continue

           try:
               class_id = int(
                   parts[0]
               )
               cx = float(
                   parts[1]
               ) * iw
               cy = float(
                   parts[2]
               ) * ih
               width = float(
                   parts[3]
               ) * iw
               height = float(
                   parts[4]
               ) * ih
           except ValueError:
               continue

           if class_id not in ID_TO_CLASS:
               continue

           x1 = cx - width / 2
           y1 = cy - height / 2
           x2 = cx + width / 2
           y2 = cy + height / 2

           self.boxes.append({
               "class":
                   class_id,
               "label":
                   ID_TO_CLASS[
                       class_id
                   ],
               "x1":
                   x1,
               "y1":
                   y1,
               "x2":
                   x2,
               "y2":
                   y2
           })

   # ========================================================
   # LIST SELECT
   # ========================================================
   def list_select(self, event):
       selection = (
           self.listbox.curselection()
       )

       if not selection:
           return

       new_index = selection[0]

       if new_index == self.index:
           return

       if not self.can_leave():
           self.listbox.selection_clear(
               0,
               tk.END
           )
           self.listbox.selection_set(
               self.index
           )
           return

       self.load_image(
           new_index
       )

   # ========================================================
   # PROGRESS
   # ========================================================
   def update_progress(self):
       saved = 0

       for file in self.files:
           image_path = (
               OUT_IMAGES /
               file.name
           )
           label_path = (
               OUT_LABELS /
               f"{file.stem}.txt"
           )

           if (
               image_path.exists()
               and
               label_path.exists()
               and
               label_path.stat().st_size > 0
           ):
               saved += 1

       self.progress.set(
           f"{self.index + 1} / "
           f"{len(self.files)}"
           f"   |   "
           f"{saved} saved"
       )

   # ========================================================
   # CANCEL
   # ========================================================
   def cancel(self):
       self.mode = None
       self.handle = None
       self.update_image()

# ============================================================
# START
# ============================================================
root = tk.Tk()
app = Annotator(root)
root.mainloop()