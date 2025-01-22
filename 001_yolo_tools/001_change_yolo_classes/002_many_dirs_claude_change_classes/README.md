# 🔄 YOLO Class Rematcher

Tool for remapping YOLO class labels while preserving folder structure and label formats.

## 🌟 Features

- 📁 Preserves directory structure
- 🔍 Supports recursive processing of nested folders
- ⚙️ YAML configuration
- 📊 Progress tracking
- 🚀 Bulk processing
- 🛡️ Error handling and logging

## 📋 Configuration

Create `config.yaml` file:

```yaml
src_labels: "/path/to/source/labels"
dst_labels: "/path/to/destination/labels"
rematch_classes:
  0: 1    # replace class 0 with 1
  1: 0    # replace class 1 with 0
  2: 8    # replace class 2 with 8
  3: 9    # replace class 3 with 9
```

## 🚀 Usage

```bash
python remap_yolo_classes.py
```

## 📁 Directory Structure Example

```
src_labels/
    └── folder1/
        ├── image1.txt
        └── image2.txt
    └── folder2/
        ├── image3.txt
        └── image4.txt

dst_labels/  # Will maintain the same structure
    └── folder1/
        ├── image1.txt  # With remapped classes
        └── image2.txt
    └── folder2/
        ├── image3.txt
        └── image4.txt
```

## 📝 Requirements

- Python 3.6+
- PyYAML
- tqdm

## 🛠️ Installation

```bash
pip install PyYAML tqdm
```