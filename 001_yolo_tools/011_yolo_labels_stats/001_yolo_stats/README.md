# YOLO Label Statistics Tool

A simple Python script to analyze YOLO format detection labels and provide class distribution statistics.

## Description
This tool analyzes label files in YOLO format and generates statistics about class distributions, including both absolute counts and percentages for each class.

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
classes:
  - "000_target_top"
  - "001_backround_top"
  - "002_strip"
  - "003_coil"
  - "004_unknown"
```

## Usage
```bash
python yolo_stats.py
```

## Output Example
```
Counts:
cl 0 000_target_top : 150
cl 1 001_backround_top : 450
cl 2 002_strip : 60
Total: 660

Percentages:
cl 0 000_target_top : 22.7%
cl 1 001_backround_top : 68.2%
cl 2 002_strip : 9.1%
```

## File Structure
- `yolo_stats.py` - Main script
- `config.yaml` - Configuration file

## License
MIT