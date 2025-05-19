#!/usr/bin/env python3
import os
import yaml
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from PIL import Image
from tqdm import tqdm

def generate_colors(n):
    """
    Generate n distinct colors for visualization
    """
    colors = []
    for i in range(n):
        # Generate bright, distinct colors using HSV color space
        hue = i / n
        saturation = 0.9
        value = 0.9
        
        # Convert HSV to RGB - plt.cm.hsv returns RGBA (4 values)
        rgba = plt.cm.hsv(hue)
        r, g, b, a = rgba  # Unpack all 4 values
        colors.append((int(r*255), int(g*255), int(b*255)))
    
    return colors

def read_classes(classes_path):
    """
    Read class names from classes.txt file
    """
    with open(classes_path, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    return classes

def draw_segmentation(img_path, label_path, output_path, class_names, colors):
    """
    Draw segmentation masks on the image
    """
    # Read the image
    img = cv2.imread(img_path)
    if img is None:
        print(f"Cannot read image: {img_path}")
        return False
    
    height, width = img.shape[:2]
    
    # Read segmentation labels
    if not os.path.exists(label_path):
        print(f"Label file not found: {label_path}")
        return False
    
    with open(label_path, 'r') as f:
        segmentation_lines = [line.strip() for line in f.readlines()]
    
    # Create figure and axes
    fig, ax = plt.subplots(1, figsize=(12, 9))
    ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Draw each segmentation
    for line in segmentation_lines:
        parts = line.strip().split()
        
        if len(parts) < 7:  # Need at least 3 points (class_idx + 6 coordinates)
            continue
            
        class_idx = int(parts[0])
        class_name = class_names[class_idx] if class_idx < len(class_names) else f"Class {class_idx}"
        color = colors[class_idx % len(colors)]
        
        # Extract coordinates
        polygon_points = []
        for i in range(1, len(parts), 2):
            if i+1 < len(parts):
                x = float(parts[i]) * width
                y = float(parts[i+1]) * height
                polygon_points.append((x, y))
        
        if len(polygon_points) < 3:
            continue
            
        # Create a polygon patch
        polygon = np.array(polygon_points)
        path = Path(polygon)
        patch = PathPatch(path, facecolor=np.array(color)/255, 
                         edgecolor=(0,0,0), alpha=0.4, lw=1.5)
        ax.add_patch(patch)
        
        # Add class label near the polygon
        centroid = np.mean(polygon, axis=0)
        ax.text(centroid[0], centroid[1], class_name, 
                color='white', fontsize=12, 
                bbox=dict(facecolor=np.array(color)/255, alpha=0.8, edgecolor='black', boxstyle='round'))
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    
    return True

def merge_images(img1_path, img2_path, output_path):
    """
    Combines two images horizontally and saves the result.
    Canvas size is determined by the larger image, and the second image
    is scaled to fill its half while maintaining proportions.
    """
    try:
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        
        # Determine size of the larger image
        img1_area = img1.width * img1.height
        img2_area = img2.width * img2.height
        
        if img1_area >= img2_area:
            base_width = img1.width
            base_height = img1.height
        else:
            base_width = img2.width
            base_height = img2.height
        
        # Create canvas twice as wide as the larger image
        canvas_width = base_width * 2
        canvas_height = base_height
        merged_img = Image.new('RGB', (canvas_width, canvas_height))
        
        # Scale first image if needed
        if img1.width != base_width or img1.height != base_height:
            # Maintain proportions, scale to fill left half
            ratio = min(base_width / img1.width, base_height / img1.height)
            new_width = int(img1.width * ratio)
            new_height = int(img1.height * ratio)
            img1_resized = img1.resize((new_width, new_height), Image.LANCZOS)
            
            # Calculate position to center the image
            left_pos = (base_width - new_width) // 2
            top_pos = (base_height - new_height) // 2
            
            # Insert first image
            merged_img.paste(img1_resized, (left_pos, top_pos))
        else:
            # Insert first image without changes
            merged_img.paste(img1, (0, 0))
        
        # Scale second image to fill right half
        # Maintain aspect ratio, fit within available space
        ratio = min(base_width / img2.width, base_height / img2.height)
        new_width = int(img2.width * ratio)
        new_height = int(img2.height * ratio)
        img2_resized = img2.resize((new_width, new_height), Image.LANCZOS)
        
        # Calculate position to center image in right half
        right_half_start = base_width
        left_pos = right_half_start + (base_width - new_width) // 2
        top_pos = (base_height - new_height) // 2
        
        # Insert second image
        merged_img.paste(img2_resized, (left_pos, top_pos))
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save result
        merged_img.save(output_path)
        return True
    except Exception as e:
        print(f"Ошибка при обработке {img1_path} и {img2_path}: {e}")
        return False

def create_sample_config(config_path):
    """
    Create a sample configuration file if none exists
    """
    sample_config = {
        'src_imgs': '/path/to/original/images',
        'src_labels': '/path/to/yolo/labels',
        'classes_txt': '/path/to/classes.txt',
        'dst_plotted': '/path/to/visualized/images',
        'combined': '/path/to/combined/images'
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False)
    
    print(f"Создан пример конфигурационного файла: {config_path}")
    print("Пожалуйста, настройте параметры и запустите скрипт снова.")

def main():
    """
    Main function that handles both segmentation visualization and image combining
    """
    # Define config path
    config_path = "config.yaml"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Ошибка: Конфигурационный файл {config_path} не найден!")
        create_sample_config(config_path)
        return
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract parameters from config
    src_imgs = config.get('src_imgs')
    src_labels = config.get('src_labels')
    classes_txt = config.get('classes_txt')
    dst_plotted = config.get('dst_plotted')
    combined_dir = config.get('combined')
    
    # Validate configuration
    required_params = ['src_imgs', 'src_labels', 'classes_txt', 'dst_plotted', 'combined']
    missing_params = [param for param in required_params if param not in config or not config[param]]
    
    if missing_params:
        print(f"Ошибка: Отсутствуют обязательные параметры в конфигурационном файле: {', '.join(missing_params)}")
        return
    
    # Validate paths
    if not os.path.isdir(src_imgs):
        print(f"Ошибка: Директория исходных изображений не существует: {src_imgs}")
        return
    
    if not os.path.isdir(src_labels):
        print(f"Ошибка: Директория с YOLO-метками не существует: {src_labels}")
        return
    
    if not os.path.exists(classes_txt):
        print(f"Ошибка: Файл классов не найден: {classes_txt}")
        return
    
    # Create output directories if they don't exist
    os.makedirs(dst_plotted, exist_ok=True)
    os.makedirs(combined_dir, exist_ok=True)
    
    # Read class names
    class_names = read_classes(classes_txt)
    print(f"Обнаружено {len(class_names)} классов: {class_names}")
    
    # Generate colors for classes
    colors = generate_colors(len(class_names))
    
    # Get list of image files
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    img_files = [f for f in os.listdir(src_imgs) 
                if os.path.splitext(f.lower())[1] in img_extensions]
    
    if not img_files:
        print(f"Изображения не найдены в {src_imgs}")
        return
    
    print(f"Обработка {len(img_files)} изображений...")
    
    # Process each image
    seg_success_count = 0
    combine_success_count = 0
    
    for img_file in tqdm(img_files, desc="Обработка изображений"):
        # Get the corresponding label file
        base_name = os.path.splitext(img_file)[0]
        label_file = f"{base_name}.txt"
        
        img_path = os.path.join(src_imgs, img_file)
        label_path = os.path.join(src_labels, label_file)
        plotted_path = os.path.join(dst_plotted, img_file)
        combined_path = os.path.join(combined_dir, img_file)
        
        # Step 1: Draw segmentation
        seg_result = draw_segmentation(img_path, label_path, plotted_path, 
                                     class_names, colors)
        if seg_result:
            seg_success_count += 1
            
            # Step 2: Combine original and plotted images
            combine_result = merge_images(img_path, plotted_path, combined_path)
            if combine_result:
                combine_success_count += 1
    
    print(f"\nОбработка завершена:")
    print(f"Визуализация сегментации: {seg_success_count}/{len(img_files)} изображений обработано")
    print(f"Объединение изображений: {combine_success_count}/{len(img_files)} изображений обработано")
    print(f"Визуализированные изображения сохранены в: {dst_plotted}")
    print(f"Объединенные изображения сохранены в: {combined_dir}")

if __name__ == "__main__":
    main()