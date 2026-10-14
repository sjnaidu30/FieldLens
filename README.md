FieldLens
Computer vision–assisted multimeter reading and validation

FieldLens is an in-progress computer vision project designed to help extract measurement readings from photographs of digital multimeters. The planned pipeline combines object detection, display-region extraction, image preprocessing, OCR, and measurement validation.
Problem Statement
Reading measurements from field photographs can be difficult when images contain perspective distortion, inconsistent lighting, reflections, or small LCD text. FieldLens explores an automated pipeline to locate the multimeter display and extract a readable measurement.
Planned Pipeline
Image input — load a photograph of a multimeter.
Object detection — detect the multimeter and its display using YOLO.
Display extraction — crop the detected display region.
Image preprocessing — prepare the crop for OCR.
OCR — extract text from the display.
Parsing and validation — interpret the extracted reading and flag uncertain or invalid results.
Current Progress
☑ Dataset split into training and validation directories

☑ Dataset pairing and validation utility scripts created

☑ Annotation tooling available in the repository

☐ Train and evaluate the object-detection model

☐ Integrate display cropping and preprocessing

☐ Integrate OCR and measurement parsing

☐ Evaluate the complete pipeline on representative images
Project status: in development. Detection accuracy and end-to-end performance have not yet been established.
Repository Structure
FieldLens/

├── README.md

├── data.yaml

├── requirements.txt

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

The local dataset is excluded from Git and must be prepared separately before training.
Setup
Clone the repository.

Create and activate a Python virtual environment.

Install dependencies from requirements.txt.

Prepare an appropriately annotated dataset in the directory structure expected by data.yaml.

Run the dataset validation scripts before training.

Example on Windows PowerShell:

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

The supported Python version and model-training dependencies must be verified for the development environment.
Dataset Format
The detection dataset uses YOLO-style annotations. Each object annotation contains a class ID and normalized bounding-box coordinates:

class_id x_center y_center width height

Class IDs:

0 — multimeter

1 — display

All coordinates and dimensions are normalized relative to the image dimensions.
Limitations
OCR accuracy and detection performance are not yet benchmarked.

Results may vary with glare, blur, perspective, lighting, and display quality.

Extracted readings require validation before they can be used operationally.
Future Work
Train and evaluate a baseline detector.

Compare preprocessing methods for LCD readability.

Add OCR confidence handling and reading validation.

Measure detection metrics, OCR accuracy, and end-to-end success rate.

Add reproducible tests and sample results.
License
No license has been specified yet. All rights and reuse permissions remain subject to the repository owner’s decision and any applicable dataset or third-party restrictions.
 