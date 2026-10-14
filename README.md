# FieldLens

## Computer Vision–Assisted Multimeter Reading and Validation

FieldLens is an in-progress computer vision project that aims to automate the extraction and validation of measurement readings from digital multimeter photographs.

The project explores an object-detection and OCR pipeline to locate a multimeter display, extract its contents, and convert the recognized text into a structured measurement.

---

## Overview

Reading multimeter values from field photographs can be challenging due to:

- Perspective distortion
- Glare and reflections
- Inconsistent lighting
- Motion blur
- Small LCD characters
- Partial display visibility

FieldLens investigates how computer vision and optical character recognition (OCR) can automate this process.

Rather than relying on a single end-to-end prediction model, the project is designed as a modular and testable pipeline.

---

## Objectives

- Detect a multimeter and its display in an input image
- Extract the display region using the detected bounding box
- Preprocess the display crop to improve readability
- Apply OCR to recognize the displayed measurement
- Parse and validate the extracted reading
- Flag uncertain or invalid results for manual review
- Evaluate performance using measurable detection and recognition metrics

---

## System Pipeline

```text
Input Photograph
      |
      v
Image Loading
      |
      v
YOLO Object Detection
      |
      +--------------------+
      |                    |
      v                    v
 Multimeter             Display
 Detection              Detection
                           |
                           v
                   Display Region Crop
                           |
                           v
                   Image Preprocessing
                           |
                           v
                          OCR
                           |
                           v
                 Measurement Parsing
                           |
                           v
                  Validation / Review
```

> **Note:** The diagram represents the intended pipeline. Components that have not yet been implemented and evaluated remain under development.

---

## Technology Stack

| Component | Technology |
|------------|------------|
| Programming Language | Python |
| Object Detection | YOLO-based detector (planned training and evaluation) |
| Image Processing | To be finalized |
| Text Recognition | OCR integration planned |
| Annotation Format | YOLO bounding-box format |
| Dataset Validation | Custom Python scripts |
| Version Control | Git and GitHub |

The exact model architecture, OCR engine, and image-processing dependencies will be documented once finalized.

---

## Repository Structure

```text
FieldLens/
├── .gitignore
├── README.md
├── requirements.txt
├── data.yaml
├── annotator.py
├── check_annotations.py
├── check_object_counts.py
├── split_dataset.py
├── scripts/
│   ├── check_split.py
│   └── validate_dataset.py
└── tools/
    └── annotator/
        └── annotator.html
```

### Dataset Policy

Training and validation images and labels are intentionally excluded from version control.

The dataset must be prepared locally before training.

The repository structure above reflects only the files currently committed to GitHub.

---

## Dataset Preparation

The dataset uses YOLO-style annotations.

Each annotation row contains:

```text
class_id x_center y_center width height
```

Bounding-box coordinates are normalized relative to image dimensions.

### Object Classes

| Class ID | Class Name |
|-----------|------------|
| 0 | multimeter |
| 1 | display |

### Expected Dataset Layout

```text
dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
```

Each image is expected to have a corresponding `.txt` annotation file with the same filename stem.

Annotation files should:

- Use valid class IDs
- Include normalized coordinates
- Match image filenames

---

## Dataset Configuration

The `data.yaml` file defines dataset paths and class names.

Example:

```yaml
path: dataset

train: images/train
val: images/val

names:
  0: multimeter
  1: display
```

Ensure these paths match your local dataset structure before training.

---

## Validation Utilities

The repository includes several scripts to validate the dataset before model training.

| Script | Purpose |
|----------|----------|
| `check_annotations.py` | Checks annotation file validity |
| `check_object_counts.py` | Summarizes object counts |
| `scripts/check_split.py` | Verifies image-label pairing |
| `scripts/validate_dataset.py` | Performs structural dataset validation |
| `split_dataset.py` | Creates training and validation splits |
| `annotator.py` | Annotation support utility |
| `tools/annotator/annotator.html` | Browser-based annotation tool |

The exact checks and supported arguments depend on each script's implementation.

---

## Setup

### Prerequisites

- Python version compatible with project dependencies
- Git
- Local copy of the repository
- Prepared YOLO-format dataset

### 1. Clone the Repository

```bash
git clone https://github.com/sjnaidu30/FieldLens.git
cd FieldLens
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Ensure that dependency versions remain compatible with the selected machine-learning and computer-vision libraries.

### 4. Prepare the Dataset

Place the dataset in the expected directory structure.

Verify:

- Matching image and label filenames
- Valid class IDs
- Normalized bounding-box coordinates

### 5. Validate the Dataset

From the repository root:

```bash
python .\scripts\check_split.py
python .\scripts\validate_dataset.py
```

Review all reported warnings or errors before beginning training.

---

## Evaluation Plan

Performance evaluation will begin once a baseline model has been trained.

### Detection Metrics

- Precision
- Recall
- Mean Average Precision (mAP)

### OCR Metrics

- Character-level accuracy
- Exact reading accuracy

### Validation Metrics

- Correct handling of invalid readings
- Correct handling of incomplete readings
- Uncertainty detection performance

### End-to-End Metrics

- Percentage of images producing a correct validated measurement

### Robustness Testing

Performance under:

- Poor lighting
- Reflections and glare
- Blur
- Perspective distortion
- Low-resolution images

> No performance claims are made until measured on an appropriate evaluation dataset.

---

## Current Development Status

### Completed

- [x] Initial repository created and connected to GitHub
- [x] Dataset split and validation scripts added
- [x] Annotation-related tooling added
- [x] Dataset excluded from version control

### In Progress

- [ ] Complete dataset structural validation
- [ ] Establish a compatible training environment
- [ ] Train and evaluate a baseline detector
- [ ] Implement display cropping and preprocessing
- [ ] Integrate OCR and measurement parsing
- [ ] Implement reading validation and uncertainty handling
- [ ] Evaluate end-to-end performance
- [ ] Document reproducible test results and example outputs

---

## Limitations

FieldLens is currently under development.

The following characteristics have not yet been established:

- Detection accuracy
- OCR accuracy
- Processing speed
- End-to-end reliability

Potential challenges include:

- LCD reflections
- Low-resolution images
- Rotated displays
- Partially obscured screens
- Ambiguous characters
- Measurement unit interpretation

Any extracted reading intended for operational use should be independently validated before being trusted.

---

## Responsible Data Handling

- Do not commit confidential company photographs or field records.
- Do not store credentials or secrets in version control.
- Keep virtual environments and generated model weights out of Git.
- Ensure third-party datasets and software libraries are used in accordance with their licenses.
- A private repository is not a substitute for permission to store or publish restricted information.

---

## Future Work

- Establish a reproducible dataset validation workflow
- Train a baseline detector and inspect predictions visually
- Compare display preprocessing strategies
- Integrate OCR and structured measurement parsing
- Add unit tests for parsing and validation
- Benchmark detection, OCR, and end-to-end performance
- Document failure cases and improve robustness

---

## License

No license has been specified.

All rights are reserved by default unless a license is added or other applicable terms apply.

Dataset permissions and third-party component licenses must be respected independently.
