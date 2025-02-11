# YOLO Training Results Analyzer

A streamlit-based tool for analyzing and visualizing YOLOv8+ (9,10,11) training results. This tool helps compare multiple training experiments by creating summary tables and interactive visualizations.

## Features

- 📊 Interactive visualization of training metrics
- 📈 Multiple plot types (normal, logarithmic, EMA smoothing)
- 📋 Automatic summary table generation
- 🔄 Support for multiple training experiments
- 📱 Responsive web interface
- 💾 Automatic results export

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/yolo-training-analyzer.git
cd yolo-training-analyzer
```

2. Install dependencies:
```bash
pip install streamlit pandas plotly pyyaml
```

## Usage

1. Create a `config.yaml` file with your paths:
```yaml
src: "path/to/results/"  # Directory containing train folders
dst: "path/to/save/"     # Directory for saving analysis results
```

2. Run the visualization:
```bash
streamlit run visualizer.py
```

### Directory Structure

The tool expects your results directory to have the following structure:
```
results/
├── train/
│   ├── args.yaml
│   └── results.csv
├── train1/
│   ├── args.yaml
│   └── results.csv
└── train2/
    ├── args.yaml
    └── results.csv
```

### Visualization Options

- **Normal**: Raw data visualization
- **Log**: Logarithmic scale visualization
- **EMA**: Exponential Moving Average smoothing
  - Adjustable smoothing factor (0.01-1.0)

### Metrics Supported

- Training Losses:
  - Box Loss
  - Classification Loss
  - DFL Loss
- Validation Metrics:
  - Precision
  - Recall
  - mAP50
  - mAP50-95
- Learning Rates:
  - lr/pg0
  - lr/pg1
  - lr/pg2

## File Description

- `visualizer.py`: Main Streamlit application for visualization
- `yolo_processor.py`: Data processing utilities for YOLO results
- `config.yaml`: Configuration file for paths

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualization powered by [Plotly](https://plotly.com/)
- Compatible with [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)