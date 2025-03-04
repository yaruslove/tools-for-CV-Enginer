# Supervisely to YOLO Format Converter

This repository contains scripts to convert annotation data between different formats:

1. `json_to_yolo.py`: Converts Supervisely JSON annotations to YOLO format
2. `script_rename.py`: Renames files by removing image extensions in filenames

## Json to YOLO Converter

The main script `json_to_yolo.py` converts Supervisely format JSON annotations to YOLO format for object detection.

### Features

- Converts rectangle bounding boxes from Supervisely JSON to YOLO format
- Automatically assigns class IDs to unique class names
- Creates a classes.txt file with class mapping
- Maintains original filename structure (removing image extensions)
- Progress bar for tracking conversion
- Input validation and error reporting

### Supervisely JSON Format

The script works with Supervisely format JSON files, which have the following structure:

```json
{
    "description": "",
    "tags": [],
    "size": {
        "height": 2000,
        "width": 2000
    },
    "objects": [
        {
            "id": 14408840,
            "classId": 20697,
            "description": "",
            "geometryType": "rectangle",
            "labelerLogin": "user@example.com",
            "createdAt": "2023-07-10T16:24:42.354Z",
            "updatedAt": "2023-07-10T16:24:42.354Z",
            "tags": [],
            "classTitle": "unripe",
            "points": {
                "exterior": [
                    [x1, y1],
                    [x2, y2]
                ],
                "interior": []
            }
        },
        ...
    ]
}
```

### YOLO Format Output

The script converts the annotations to YOLO format, where each object is represented as:

```
<class_id> <x_center> <y_center> <width> <height>
```

All values are normalized to be between 0 and 1 relative to the image dimensions.

## Installation

```bash
git clone https://github.com/yourusername/supervisely-to-yolo.git
cd supervisely-to-yolo
pip install -r requirements.txt
```

## Requirements

- Python 3.6+
- pyyaml
- tqdm

## Usage

### 1. Configure the script

Create a configuration file `json_to_yolo_config.yaml` with the following content:

```yaml
src: '/path/to/supervisely_json_files'
dst: '/path/to/yolo_files_output'
```

### 2. Run the converter

```bash
python json_to_yolo.py
```

The script will:
1. Analyze all JSON files to extract class names
2. Create a mapping from class names to numeric IDs
3. Convert each JSON file to a corresponding YOLO format text file
4. Create a `classes.txt` file in the destination directory

### 3. Check the output

The output directory will contain:
- YOLO format `.txt` files for each input JSON file
- A `classes.txt` file with the mapping between class IDs and names

## File Renaming Script

The repository also includes `script_rename.py` for renaming files by removing image extensions from filenames.

### Usage

```bash
python script_rename.py
```

Configure the paths in `rename_config.yaml`:

```yaml
src: '/path/to/source_files'
dst: '/path/to/destination_files'
```

This script will convert filenames like:
- `IMG_1232.jpg.json` → `IMG_1232.json`
- `IMG_1232.jpg.txt` → `IMG_1232.txt`

## License

[MIT](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.