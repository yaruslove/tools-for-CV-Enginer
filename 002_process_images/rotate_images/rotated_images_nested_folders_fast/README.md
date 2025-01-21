# Image Rotator 🔄

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Powerful and easy-to-use tool for batch rotating images in nested directories while preserving folder structure.

<img src="/api/placeholder/800/400" alt="Directory Structure Example" />

## 🌟 Features

- **Recursive Processing**: Automatically handles nested folder structures
- **Structure Preservation**: Maintains original folder hierarchy in the destination
- **Format Support**: Works with multiple image formats (JPG, JPEG, PNG, BMP, GIF)
- **Quality Preservation**: Maintains image quality during rotation
- **Error Handling**: Robust error handling and progress reporting

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/image-rotator.git
cd image-rotator
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `config.yaml` file with the following structure:

```yaml
src: "path/to/source/folder"
dst: "path/to/destination/folder"
angle: 90  # rotation angle clockwise in degrees
```

### Example Directory Structure:

```
source_folder/
├── wedding/
│   ├── ceremony/
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
│   └── reception/
│       ├── photo3.jpg
│       └── photo4.jpg
└── vacation/
    ├── beach/
    │   └── photo5.jpg
    └── mountain/
        └── photo6.jpg
```

After processing:

```
destination_folder/
├── wedding/
│   ├── ceremony/
│   │   ├── photo1.jpg  # rotated
│   │   └── photo2.jpg  # rotated
│   └── reception/
│       ├── photo3.jpg  # rotated
│       └── photo4.jpg  # rotated
└── vacation/
    ├── beach/
    │   └── photo5.jpg  # rotated
    └── mountain/
        └── photo6.jpg  # rotated
```

## 🎯 Usage

1. Configure your settings in `config.yaml`
2. Run the script:
```bash
python image_rotator.py
```

### Visual Example

Before rotation:

<img src="/api/placeholder/400/300" alt="Before Rotation" />

After rotation (90° clockwise):

<img src="/api/placeholder/300/400" alt="After Rotation" />

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Requirements

- Python 3.6+
- Pillow
- PyYAML

## 💡 Advanced Usage

### Custom Angle Presets

You can use common angle presets:
- 90° - Rotate right
- 180° - Flip
- 270° - Rotate left

Example config with 270° rotation:
```yaml
src: "path/to/source/folder"
dst: "path/to/destination/folder"
angle: 270  # This will rotate images left
```

### Error Handling

The script provides detailed error messages and continues processing even if individual files fail:

```python
try:
    process_images(...)
except Exception as e:
    print(f"Error: {str(e)}")
```

## 📊 Performance

The script processes images sequentially to ensure stability. For large directories, progress is displayed in real-time:

```
Processing: wedding/ceremony/photo1.jpg -> Done
Processing: wedding/ceremony/photo2.jpg -> Done
...
```

## 🔍 Troubleshooting

Common issues and solutions:

1. **Permission Error**:
   - Ensure you have write permissions in the destination folder
   - Run the script with appropriate permissions

2. **Memory Error**:
   - Process fewer images at once
   - Ensure sufficient system resources

3. **Format Error**:
   - Verify image format is supported
   - Check file extensions are lowercase

## 📬 Contact

Your Name - [@yourusername](https://twitter.com/yourusername)

Project Link: [https://github.com/yourusername/image-rotator](https://github.com/yourusername/image-rotator)
