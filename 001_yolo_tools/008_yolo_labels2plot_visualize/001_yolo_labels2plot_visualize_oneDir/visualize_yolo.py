import os
import yaml
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import logging
from collections import defaultdict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Statistics:
    def __init__(self):
        self.total_images = 0
        self.processed_images = 0
        self.images_with_labels = 0
        self.images_without_labels = 0
        self.total_boxes = 0
        self.boxes_per_class = defaultdict(int)
        self.failed_images = []
        self.missing_labels = []
    
    def print_report(self, class_names):
        print("\n=== Processing Statistics ===")
        print(f"Total images found: {self.total_images}")
        print(f"Successfully processed images: {self.processed_images}")
        print(f"Images with labels: {self.images_with_labels}")
        print(f"Images without labels: {self.images_without_labels}")
        print(f"Total bounding boxes: {self.total_boxes}")
        print("\nBoxes per class:")
        for class_id, count in self.boxes_per_class.items():
            print(f"class_id: {class_id}")
            class_name = class_names[class_id]
            print(f"  {class_name}: {count}")
        if self.failed_images:
            print("\nFailed to process images:")
            for img in self.failed_images:
                print(f"  {img}")
        if self.missing_labels:
            print("\nMissing label files:")
            for img in self.missing_labels:
                print(f"  {img}")

def load_config(config_path):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
            # Set default values if not provided
            config.setdefault('box_thickness', 2)
            config.setdefault('font_scale', 0.6)
            config.setdefault('font_thickness', 2)
            
            logging.info(f"Loaded configuration from {config_path}")
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise

def validate_config(config):
    """Validate configuration parameters and paths"""
    # Проверка наличия необходимых параметров
    required_params = ['src_imgs', 'src_labels', 'dst_imgs', 'classes', 'colors']
    missing_params = [param for param in required_params if param not in config]
    if missing_params:
        raise ValueError(f"Missing required parameters: {missing_params}")

    # Проверка соответствия количества классов и цветов
    if len(config['classes']) != len(config['colors']):
        raise ValueError(
            f"Number of classes ({len(config['classes'])}) "
            f"doesn't match number of colors ({len(config['colors'])})"
        )

    # Проверка путей
    if not os.path.exists(config['src_imgs']):
        raise FileNotFoundError(f"Source images directory not found: {config['src_imgs']}")
    
    if not os.path.exists(config['src_labels']):
        raise FileNotFoundError(f"Source labels directory not found: {config['src_labels']}")
    
    # Проверка параметров отрисовки
    if not isinstance(config['box_thickness'], (int, float)) or config['box_thickness'] <= 0:
        raise ValueError("box_thickness must be positive number")
    if not isinstance(config['font_scale'], (int, float)) or config['font_scale'] <= 0:
        raise ValueError("font_scale must be positive number")
    if not isinstance(config['font_thickness'], (int, float)) or config['font_thickness'] <= 0:
        raise ValueError("font_thickness must be positive number")

    # Создание выходной директории
    try:
        Path(config['dst_imgs']).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise Exception(f"Cannot create destination directory: {str(e)}")

    # Проверка валидности цветов
    for i, color in enumerate(config['colors']):
        if not isinstance(color, list) or len(color) != 3 or \
           not all(isinstance(c, (int, float)) and 0 <= c <= 255 for c in color):
            raise ValueError(f"Invalid color format for class {config['classes'][i]}: {color}")
        config['colors'][i] = [int(c) for c in color]

def draw_boxes(image, boxes, class_names, colors, box_thickness, font_scale, font_thickness):
    """Draw bounding boxes and labels on image"""
    height, width = image.shape[:2]
    
    for box in boxes:
        try:
            class_id, x, y, w, h = box
            class_id = int(class_id)
            
            if class_id >= len(class_names):
                logging.warning(f"Invalid class ID {class_id}, skipping box")
                continue
            
            if not all(0 <= coord <= 1 for coord in [x, y, w, h]):
                logging.warning(f"Invalid coordinates {[x, y, w, h]}, skipping box")
                continue
            
            # Convert normalized coordinates to pixel coordinates
            x1 = int((x - w/2) * width)
            y1 = int((y - h/2) * height)
            x2 = int((x + w/2) * width)
            y2 = int((y + h/2) * height)
            
            color = colors[class_id]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, box_thickness)
            
            label = class_names[class_id]
            
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
            )
            
            cv2.rectangle(
                image, 
                (x1, y1 - text_height - baseline), 
                (x1 + text_width, y1),
                color, 
                -1
            )
            
            cv2.putText(
                image, 
                label,
                (x1, y1 - baseline),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                font_thickness
            )
        except Exception as e:
            logging.error(f"Error drawing box: {str(e)}, box data: {box}")
            continue
    
    return image

def process_images(config):
    """Process all images and draw bounding boxes"""
    stats = Statistics()
    
    try:
        img_files = sorted([
            f for f in os.listdir(config['src_imgs']) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
        ])
        stats.total_images = len(img_files)
        logging.info(f"Found {stats.total_images} images to process")
    except Exception as e:
        logging.error(f"Error listing image files: {str(e)}")
        raise

    colors = {i: tuple(config['colors'][i]) for i in range(len(config['classes']))}
    
    for img_file in tqdm(img_files, desc="Processing images"):
        try:
            # Load image
            img_path = os.path.join(config['src_imgs'], img_file)
            image = cv2.imread(img_path)
            if image is None:
                logging.error(f"Could not load image: {img_path}")
                stats.failed_images.append(img_file)
                continue
            
            # Get label file path
            label_file = os.path.join(
                config['src_labels'], 
                os.path.splitext(img_file)[0] + '.txt'
            )
            
            boxes = []
            if os.path.exists(label_file):
                stats.images_with_labels += 1
                with open(label_file, 'r') as f:
                    for line in f.readlines():
                        try:
                            values = list(map(float, line.strip().split()))
                            if len(values) == 5:
                                class_id = int(values[0])

                                boxes.append(values)
                                stats.total_boxes += 1
                                stats.boxes_per_class[class_id] += 1
                            else:
                                logging.warning(f"Invalid label format in {label_file}: {line}")
                        except Exception as e:
                            logging.error(f"Error parsing label in {label_file}: {str(e)}")
            else:
                stats.images_without_labels += 1
                stats.missing_labels.append(img_file)
                logging.warning(f"Label file not found: {label_file}")
            
            # Draw boxes
            image = draw_boxes(
                image, boxes, config['classes'], colors,
                config['box_thickness'], config['font_scale'], config['font_thickness']
            )
            
            # Save processed image
            output_path = os.path.join(config['dst_imgs'], img_file)
            if not cv2.imwrite(output_path, image):
                logging.error(f"Failed to save image: {output_path}")
                stats.failed_images.append(img_file)
                continue
            
            stats.processed_images += 1
            
        except Exception as e:
            logging.error(f"Error processing {img_file}: {str(e)}")
            stats.failed_images.append(img_file)
            continue
    
    return stats

def main():
    config_path = 'config.yaml'
    try:
        config = load_config(config_path)
        validate_config(config)
        stats = process_images(config)
        stats.print_report(config['classes'])
        logging.info("Processing completed successfully!")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()