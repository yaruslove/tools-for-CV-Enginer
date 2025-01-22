# 🎯 Nested YOLO Label Visualizer

Simple yet powerful tool for visualizing YOLO format labels on images with support for nested directory structures and customizable styling.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- 📊 Visualize YOLO format labels (.txt) on images
- 📁 Support for nested directory structures
- 🎨 Customizable colors for each class
- 📏 Adjustable box and font settings
- 📈 Detailed processing statistics
- 🔄 Preserves multi-level directory structure

## 📁 Directory Structure

The tool expects the following directory structure:

```
src_imgs/
    directory1/
        image1.jpg
        image2.jpg
    directory2/
        image3.jpg
        image4.jpg

src_labels/
    directory1/
        image1.txt
        image2.txt
    directory2/
        image3.txt
        image4.txt

dst_imgs/  (created automatically)
    directory1/
        image1.jpg (with visualized boxes)
        image2.jpg (with visualized boxes)
    directory2/
        image3.jpg (with visualized boxes)
        image4.jpg (with visualized boxes)
```

## ⚙️ Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `config.yaml`:
```yaml
src_imgs: "path/to/base/images/directory"
src_labels: "path/to/base/labels/directory"
dst_imgs: "path/to/output/directory"
classes:
  - "class1"
  - "class2"
  - "class3"
  - "class4"
colors:
  - [0, 0, 255]     # red
  - [171, 0, 111]   # purple
  - [255, 0, 18]    # blue
  - [236, 255, 1]   # yellow

# Optional display settings
box_thickness: 4     # box line thickness
font_scale: 2        # font size
font_thickness: 4    # font line thickness
```

3. Run visualization:
```bash
python visualize_yolo.py
```

## 📊 Statistics Output

After processing, you'll get detailed statistics including:
```
=== Processing Statistics ===
Total images found: 128
Successfully processed images: 128
Images with labels: 128
Images without labels: 0
Total bounding boxes: 512
Processed directories: 2

Processed directories:
  - directory1
  - directory2

Boxes per class:
  class1: 128
  class2: 128
  class3: 128
  class4: 128
```

## 🛠️ Requirements

- Python 3.6+
- OpenCV
- PyYAML
- tqdm

## 📝 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

1. Ensure your code matches the existing style
2. Update documentation as needed
3. Add comments for complex operations
4. Test thoroughly before submitting PR

## 🚨 Common Issues

1. **Missing Label Directories**: Each image directory must have a corresponding directory in the labels path
2. **File Naming**: Label files must match image names (except extension)
3. **Directory Permissions**: Ensure write permissions for output directory
4. **Memory Usage**: For large datasets, monitor memory usage

## 🔍 Debugging Tips

- Enable debug logging for more detailed output
- Check the statistics output for processing issues
- Verify directory permissions and structure
- Ensure label format matches YOLO specifications