# Random Image Cropper 🖼️
random crop, random crop bbox image
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Fast and efficient tool for generating random crops from images using OpenCV and parallel processing.

<img src="/api/placeholder/800/400" alt="Example of random crops from images" />

## 🚀 Features

- High-performance image processing using OpenCV
- Parallel processing for faster execution
- Support for multiple image formats (JPG, JPEG, PNG, BMP)
- Configurable crop sizes and quantities
- Unique filename generation for each crop
- Cross-platform compatibility

## 📋 Requirements

- Python 3.7+
- OpenCV-Python
- NumPy

Install dependencies using:

```bash
pip install -r requirements.txt
```

## 💻 Usage

### As a Module

```python
from random_cropper import random_crop_images

random_crop_images(
    path_in="input_images",
    path_out="output_crops",
    n_crops=10,
    max_size=800,
    min_size=200
)
```

### As a Script

```bash
python random_cropper.py --path_in input_images --path_out output_crops --n_crops 10 --max_size 800 --min_size 200
```

### Parameters

| Parameter | Description | Type |
|-----------|-------------|------|
| `path_in` | Input directory with source images | `str` |
| `path_out` | Output directory for crops | `str` |
| `n_crops` | Number of crops to generate | `int` |
| `max_size` | Maximum size of crop side | `int` |
| `min_size` | Minimum size of crop side | `int` |

## 🎯 Examples

Here's an example of input image and resulting random crops:

<img src="/api/placeholder/800/300" alt="Example of input and output images comparison" />

### Code Example with Custom Parameters

```python
from random_cropper import random_crop_images

# Generate 20 square crops
random_crop_images(
    path_in="wedding_photos",
    path_out="wedding_crops",
    n_crops=20,
    max_size=1024,
    min_size=512
)
```

## 🏗️ Project Structure

```
random-image-cropper/
├── random_cropper.py     # Main script
├── requirements.txt      # Dependencies
├── tests/               # Unit tests
├── examples/            # Example usage
└── README.md           # This file
```

## ⚡ Performance

The script utilizes parallel processing through `ThreadPoolExecutor`, making it highly efficient for bulk operations. Here's a performance comparison:

<img src="/api/placeholder/600/300" alt="Performance comparison chart" />

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

If you have any questions or suggestions, feel free to open an issue or contact me:

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🌟 Acknowledgments

- OpenCV team for their amazing computer vision library
- Python community for continuous support and inspiration
- All contributors who help improve this project