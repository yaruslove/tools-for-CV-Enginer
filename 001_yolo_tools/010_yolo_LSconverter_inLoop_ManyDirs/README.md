# 🔄 YOLO to Label Studio Batch Converter

Powerful tool for batch conversion of multiple YOLO datasets to Label Studio format with automatic directory structure handling.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![Label Studio Converter](https://img.shields.io/badge/label--studio--converter-required-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Overview

This script automates the process of converting multiple YOLO-format datasets to Label Studio format, maintaining directory structure and handling paths automatically.

## ✨ Features

- 🗂️ Batch processing of multiple YOLO datasets
- 📁 Automatic directory structure preservation
- 🔍 Detailed logging and error reporting
- ⚙️ YAML-based configuration
- 🛡️ Path validation and error handling
- 🚀 Easy to use with minimal setup

## 📁 Directory Structure

### Input Structure
```
src_yolo/
    dataset1/
        images/
        labels/
    dataset2/
        images/
        labels/
    dataset3/
        images/
        labels/
```

### Output Structure
```
dst_LabelStudio/
    dataset1/
        dataset1.json
    dataset2/
        dataset2.json
    dataset3/
        dataset3.json
```

## ⚙️ Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd yolo-to-labelstudio-converter
```

2. Install required dependencies:
```bash
pip install pyyaml label-studio-converter
```

## 📝 Configuration

Create `config.yaml` with your paths:

```yaml
src_yolo: "/path/to/yolo/datasets"
dst_LabelStudio: "/path/to/labelstudio/output"
```

Example:
```yaml
src_yolo: "/data/projects/datasets/yolo_data"
dst_LabelStudio: "/data/projects/labelstudio/converted"
```

## 🚀 Usage

1. Configure paths in `config.yaml`
2. Run the script:
```bash
python converter-script.py
```

The script will:
- Validate all paths
- Create necessary output directories
- Process each dataset
- Generate detailed logs

## 📋 Requirements

- Python 3.6+
- label-studio-converter
- PyYAML
- Access rights to source and destination directories

## 🔍 Logging

The script provides detailed logging:
```
2025-01-22 10:30:15 - INFO - Loading configuration from config.yaml
2025-01-22 10:30:15 - INFO - Found 3 directories to process
2025-01-22 10:30:15 - INFO - Processing dataset1...
2025-01-22 10:30:16 - INFO - Successfully converted dataset1
...
```

## 🚨 Troubleshooting

### Common Issues

1. **FileNotFoundError**:
   - Check if source directory exists
   - Verify external drive is mounted
   - Check path spelling in config.yaml

2. **Permission Error**:
   - Verify read permissions for source directory
   - Verify write permissions for destination directory

3. **Conversion Error**:
   - Check YOLO format correctness
   - Verify image files presence
   - Check label-studio-converter installation

### Debug Mode

For more detailed output, modify logging level in script:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more details
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 🛠️ Advanced Usage

### Custom Image Root URL

The default image root URL format is:
```
/data/local-files/?d={dataset_name}/images
```

### Error Handling

The script continues processing even if one dataset fails:
- Logs errors for failed conversions
- Continues with remaining datasets
- Provides summary at completion

## 📊 Performance

- Processes datasets sequentially
- Memory usage depends on dataset size
- Creates backup of existing files before overwriting

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ✨ Future Improvements

- [ ] Parallel processing support
- [ ] Custom error handlers
- [ ] Progress bar integration
- [ ] Configuration validation
- [ ] Backup functionality

## 📫 Support

For issues and feature requests, please create an issue in the repository.