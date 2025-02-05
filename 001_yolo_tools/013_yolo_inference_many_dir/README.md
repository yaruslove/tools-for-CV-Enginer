# YOLO Inference Processing Tool

A Python script for batch processing images using YOLOv8 model with customizable detection parameters. The tool processes multiple folders of images and organizes detection results in a structured output directory.

## Features
- Processes multiple image folders in batch
- Configurable YOLO detection parameters
- Maintains original image directory structure
- Generates three output categories for each folder

## Requirements
- Python 3.x
- ultralytics
- PyYAML
- OpenCV

## Installation
```bash
pip install ultralytics pyyaml opencv-python
```

## Input Structure
```
src/
├── folder1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── folder2/
│   ├── image1.jpg
│   └── image2.jpg
└── folder3/
    └── *.jpg
```
Each subfolder in the source directory should contain images for processing.

## Output Structure
```
dst/
├── folder1/
│   ├── imgs/         # Original images
│   ├── imgs_drawed/  # Images with detection boxes
│   └── labels/       # YOLO format labels
└── folder2/
    ├── imgs/
    ├── imgs_drawed/
    └── labels/
```

## Configuration
Create a `config.yaml` file:
```yaml
weights_yolo: "path/to/weights.pt"
src: "path/to/source/folders"
dst: "path/to/output"
classes: [0, 1]  # Optional class filtering

model_params:
  agnostic_nms: true
  conf: 0.20
  iou: 0.2
  show_conf: true
```

### Parameters
- `weights_yolo`: Path to YOLO model weights
- `src`: Source directory containing image folders
- `dst`: Output directory for results
- `classes`: List of classes to detect (optional)
- `model_params`:
  - `agnostic_nms`: Class-agnostic NMS
  - `conf`: Confidence threshold
  - `iou`: IoU threshold for NMS
  - `show_conf`: Show confidence scores on boxes

## Usage
```bash
python inference.py
```

## License
MIT

## Author
[Your Name]