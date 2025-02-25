import os
import yaml
import cv2
import numpy as np
from pathlib import Path

def load_config(config_path):
    """
    Load the YAML configuration file
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def load_classes(classes_path):
    """
    Load class names from a text file
    """
    with open(classes_path, 'r') as file:
        classes = [line.strip() for line in file.readlines()]
    return classes

def create_output_dirs(output_path, classes):
    """
    Create directories for each class to store cropped images
    """
    for class_name in classes:
        class_dir = os.path.join(output_path, class_name)
        os.makedirs(class_dir, exist_ok=True)
    return

def parse_yolo_segment(label_line, img_width, img_height):
    """
    Parse YOLO segment format and convert to pixel coordinates
    Format: <class-index> <x1> <y1> <x2> <y2> ... <xn> <yn>
    """
    values = label_line.strip().split()
    class_index = int(values[0])
    
    # Convert normalized coordinates to pixel coordinates
    points = []
    for i in range(1, len(values), 2):
        if i + 1 < len(values):
            x = float(values[i]) * img_width
            y = float(values[i+1]) * img_height
            points.append([int(x), int(y)])
    
    return class_index, np.array(points, dtype=np.int32)

def crop_segment(image, points):
    """
    Crop the segment from the image using a mask
    """
    # Create a binary mask from the points
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    
    # Make sure we have at least 3 points for a polygon
    if len(points) < 3:
        print(f"Warning: Not enough points to create a polygon. Points: {points}")
        # Return None if we can't create a proper polygon
        return None
    
    # Create a properly shaped array for fillPoly
    pts = points.reshape((-1, 1, 2))
    
    # Fill the polygon with white on the mask
    cv2.fillPoly(mask, [pts], 255)
    
    # Get the bounding box of the segment
    x, y, w, h = cv2.boundingRect(points)
    
    # Make sure the bounding box has some minimum size
    if w < 3 or h < 3:
        print(f"Warning: Bounding box too small: {w}x{h}")
        # Return None for too small bounding boxes
        return None
    
    # Crop the image to the bounding box
    cropped = image[y:y+h, x:x+w].copy()
    
    # Create a mask of the same size as the cropped image
    mask_cropped = mask[y:y+h, x:x+w]
    
    # Debug: check if the mask has any non-zero values
    if np.sum(mask_cropped) == 0:
        print(f"Warning: Empty mask after cropping. Points: {points}, Bbox: {x},{y},{w},{h}")
        return None
    
    # Apply the mask to the cropped image
    if len(cropped.shape) == 3 and cropped.shape[2] == 3:
        # Create a transparent background for RGB images
        result = np.zeros((h, w, 4), dtype=np.uint8)
        # Copy the RGB channels
        result[:, :, 0:3] = cropped
        # Set alpha channel from mask
        result[:, :, 3] = mask_cropped
        return result
    elif len(cropped.shape) == 3 and cropped.shape[2] == 4:
        # If image already has alpha channel
        result = cropped.copy()
        # Apply mask to alpha channel
        result[:, :, 3] = np.where(mask_cropped > 0, cropped[:, :, 3], 0)
        return result
    else:
        print(f"Warning: Unexpected image shape: {cropped.shape}")
        return None

def process_images(config):
    """
    Process all images and their labels to crop segments
    """
    images_path = config['path_images']
    labels_path = config['path_labels']
    classes_path = config['path_classes']
    output_path = config['path_cropp']
    
    # Load classes and create output directories
    classes = load_classes(classes_path)
    create_output_dirs(output_path, classes)
    
    # Get all label files
    label_files = [f for f in os.listdir(labels_path) if f.endswith('.txt')]
    
    processed_count = 0
    skipped_count = 0
    
    for label_file in label_files:
        # Construct the image file path with various possible extensions
        image_extensions = ['.jpg', '.png', '.jpeg']
        image_file = None
        
        for ext in image_extensions:
            img_name = os.path.splitext(label_file)[0] + ext
            if os.path.exists(os.path.join(images_path, img_name)):
                image_file = img_name
                break
        
        if image_file is None:
            print(f"Warning: No matching image found for label {label_file}")
            continue
        
        # Load image
        img_path = os.path.join(images_path, image_file)
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Warning: Failed to load image {img_path}")
            continue
        
        img_height, img_width = img.shape[:2]
        
        # Read and process each segment in the label file
        with open(os.path.join(labels_path, label_file), 'r') as file:
            for line_idx, line in enumerate(file):
                try:
                    class_idx, points = parse_yolo_segment(line, img_width, img_height)
                    
                    if len(points) < 3:
                        print(f"Warning: Skipping segment with less than 3 points in {label_file}, line {line_idx+1}")
                        skipped_count += 1
                        continue
                    
                    if class_idx >= len(classes):
                        print(f"Warning: Class index {class_idx} out of range in {label_file}, line {line_idx+1}")
                        skipped_count += 1
                        continue
                    
                    # Crop the segment
                    cropped = crop_segment(img, points)
                    
                    if cropped is None:
                        print(f"Warning: Failed to crop segment in {label_file}, line {line_idx+1}")
                        skipped_count += 1
                        continue
                    
                    # Save the cropped segment
                    class_name = classes[class_idx]
                    output_dir = os.path.join(output_path, class_name)
                    output_file = f"{os.path.splitext(image_file)[0]}_seg{line_idx}.png"
                    output_path_full = os.path.join(output_dir, output_file)
                    
                    # Ensure output directory exists
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Save with PNG to preserve transparency
                    cv2.imwrite(output_path_full, cropped)
                    
                    processed_count += 1
                    
                    # Print progress for every 100 segments
                    if processed_count % 100 == 0:
                        print(f"Processed {processed_count} segments so far...")
                
                except Exception as e:
                    print(f"Error processing segment in {label_file}, line {line_idx+1}: {str(e)}")
                    skipped_count += 1
                    continue
    
    print(f"Processing complete. Successfully processed {processed_count} segments.")
    print(f"Skipped {skipped_count} segments due to errors or invalid data.")

def main():
    path_config = "config.yaml"
    
    # Load configuration
    config = load_config(path_config)
    
    # Process images
    process_images(config)

if __name__ == "__main__":
    main()