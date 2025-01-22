# 📂 YOLO Dataset Reorganizer

Simple tool for reorganizing YOLO dataset directory structure with automatic file copying and validation.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- 📁 Automatic directory structure creation
- 🔄 Smart file copying with validation
- 📊 Progress tracking and detailed logging
- ⚙️ YAML-based configuration
- ✅ Automatic verification of copied files
- 🛡️ Error handling and reporting

## 📁 Directory Structure

### Input Structure:
```
src_imgs/
    dir1/
        image1.jpg
        image2.jpg
    dir2/
        image3.jpg
        image4.jpg

src_labels/
    dir1/
        image1.txt
        image2.txt
    dir2/
        image3.txt
        image4.txt

src_classes/
    classes.txt
```

### Output Structure:
```
joined/
    dir1/
        images/
            image1.jpg
            image2.jpg
        labels/
            image1.txt
            image2.txt
        classes.txt
    dir2/
        images/
            image3.jpg
            image4.jpg
        labels/
            image3.txt
            image4.txt
        classes.txt
```

## ⚙️ Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `config.yaml`:
```yaml
src_imgs: "/path/to/source/images"
src_labels: "/path/to/source/labels"
src_classes: "/path/to/classes.txt"
joined: "/path/to/output/directory"
```

3. Run the script:
```bash
python reorganize_data.py
```

## 🛠️ Requirements

```
pyyaml>=5.1
tqdm>=4.45.0
```

## 📝 Usage Example

1. Create config.yaml:
```yaml
src_imgs: "/data/raw/images"
src_labels: "/data/raw/labels"
src_classes: "/data/classes.txt"
joined: "/data/processed"
```

2. Run the script:
```bash
python reorganize_data.py
```

3. Check the logs:
```
2025-01-22 10:30:15 - INFO - Configuration loaded from config.yaml
2025-01-22 10:30:15 - INFO - Found 2 subdirectories to process
2025-01-22 10:30:16 - INFO - Processing completed successfully
```

## 🚨 Common Issues

1. **File Permissions**: Ensure write permissions for output directory
2. **Missing Files**: Verify all source paths exist
3. **Disk Space**: Check available space in destination
4. **File Name Matching**: Ensure image and label files have matching names

## 🔍 Debugging

The script provides detailed logging:
- Check terminal output for progress and errors
- All operations are logged with timestamps
- Verification step reports any mismatches
- Progress bars show current operation status

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Update documentation as needed
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Known Limitations

- Supports only YOLO format datasets
- Single classes.txt file for all subdirectories
- No support for nested subdirectories beyond one level

## 🔮 Future Improvements

- [ ] Add support for multiple classes files
- [ ] Implement parallel processing for large datasets
- [ ] Add data validation and integrity checks
- [ ] Support for nested directory structures