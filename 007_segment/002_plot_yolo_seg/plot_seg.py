import os
import yaml
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import random
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

def main():
    # Read configuration from YAML file
    config_path = "config.yaml"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found!")
        print("Creating a sample configuration file...")
        
        # Create a sample configuration file
        sample_config = {
            'src_imgs': '/path/to/images',
            'src_labels': '/path/to/labels',
            'classes_txt': '/path/to/classes.txt',
            'dst_plotted': '/path/to/output_plotted_images'
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False)
        
        print(f"Sample configuration file created at {config_path}")
        print("Please update the configuration and run the script again.")
        return
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract parameters from config
    src_imgs = config.get('src_imgs')
    src_labels = config.get('src_labels')
    classes_txt = config.get('classes_txt')
    dst_plotted = config.get('dst_plotted')
    
    # Validate configuration
    if not all([src_imgs, src_labels, classes_txt, dst_plotted]):
        print("Error: Missing required parameters in configuration file.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(dst_plotted, exist_ok=True)
    
    # Read class names
    if not os.path.exists(classes_txt):
        print(f"Error: Classes file not found: {classes_txt}")
        return
        
    class_names = read_classes(classes_txt)
    print(f"Found {len(class_names)} classes: {class_names}")
    
    # Generate colors for classes
    colors = generate_colors(len(class_names))
    
    # Get list of image files
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    img_files = [f for f in os.listdir(src_imgs) 
                if os.path.splitext(f.lower())[1] in img_extensions]
    
    if not img_files:
        print(f"No image files found in {src_imgs}")
        return
    
    print(f"Processing {len(img_files)} images...")
    
    # Process each image
    success_count = 0
    for img_file in tqdm(img_files, desc="Visualizing"):
        # Get the corresponding label file
        base_name = os.path.splitext(img_file)[0]
        label_file = f"{base_name}.txt"
        
        img_path = os.path.join(src_imgs, img_file)
        label_path = os.path.join(src_labels, label_file)
        output_path = os.path.join(dst_plotted, f"{base_name}_segmentation.jpg")
        
        # Draw segmentation
        result = draw_segmentation(img_path, label_path, output_path, 
                                  class_names, colors)
        if result:
            success_count += 1
    
    print(f"Visualization complete. {success_count}/{len(img_files)} images processed.")
    print(f"Output saved to: {dst_plotted}")

if __name__ == "__main__":
    main()