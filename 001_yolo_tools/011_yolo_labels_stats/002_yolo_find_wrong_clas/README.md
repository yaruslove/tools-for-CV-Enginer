# YOLO Label Finder

A Python utility to find YOLO format label files containing a specific class ID.

## Description
This tool scans through YOLO format label files and identifies all files that contain annotations for a specified class ID.

## Requirements
- Python 3.x
- PyYAML

## Installation
```bash
pip install pyyaml
```

## Configuration
Create a `config.yaml` file with the following structure:
```yaml
path_labels: "path/to/your/labels/folder"
class_id: 4  # The class ID you want to find
```

## Usage
```bash
python finder_label.py
```

## Output Example
```
Files containing class_id 4:
image001.txt
image002.txt
image003.txt
...
Total files: 15
```

## File Structure
- `finder_label.py` - Main script
- `config.yaml` - Configuration file

## License
MIT