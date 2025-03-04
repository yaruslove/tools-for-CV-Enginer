import os
import yaml
import cv2
import numpy as np
import random
from pathlib import Path
from scipy.ndimage import binary_erosion, binary_dilation
import math
from tqdm import tqdm

def load_config(config_path):
    """
    Load the YAML configuration file
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def create_output_dir(output_path):
    """
    Create output directory if it doesn't exist
    """
    os.makedirs(output_path, exist_ok=True)
    return

def random_crop(image, min_size, max_size):
    """
    Extract a random crop from the image with size between min_size and max_size
    """
    h, w = image.shape[:2]
    
    # Randomly choose crop dimensions
    crop_w = random.randint(min_size[0], min(max_size[0], w))
    crop_h = random.randint(min_size[1], min(max_size[1], h))
    
    # Calculate valid positions for the crop
    max_left = w - crop_w
    max_top = h - crop_h
    
    if max_left < 0 or max_top < 0:
        print(f"Warning: Image too small ({w}x{h}) for minimum crop size {min_size}")
        return None
    
    # Randomly choose top-left corner
    left = random.randint(0, max_left)
    top = random.randint(0, max_top)
    
    # Extract the crop
    crop = image[top:top+crop_h, left:left+crop_w].copy()
    
    return crop

def create_irregular_circle_mask(width, height, irregularity=0.3, spikiness=0.2):
    """
    Create an irregular circle-like mask
    """
    center_x = width // 2
    center_y = height // 2
    radius = min(width, height) // 2 * random.uniform(0.7, 0.95)
    
    # Create points around the circle
    num_points = random.randint(10, 20)
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    
    # Add random variations to the radius
    radii = np.ones(num_points) * radius
    radii = radii * (1 + irregularity * (np.random.random(num_points) - 0.5))
    
    # Add spikes
    if random.random() < spikiness:
        spike_indices = random.sample(range(num_points), k=random.randint(1, 3))
        for idx in spike_indices:
            radii[idx] *= random.uniform(1.1, 1.3)
    
    # Calculate points
    points = []
    for i in range(num_points):
        x = center_x + int(radii[i] * np.cos(angles[i]))
        y = center_y + int(radii[i] * np.sin(angles[i]))
        points.append([x, y])
    
    # Create mask
    mask = np.zeros((height, width), dtype=np.uint8)
    points_array = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points_array], 255)
    
    return mask

def create_irregular_oval_mask(width, height, irregularity=0.2):
    """
    Create an irregular oval-like mask
    """
    center_x = width // 2
    center_y = height // 2
    
    # Random aspect ratio for the oval
    aspect_ratio = random.uniform(1.2, 2.0)
    if random.random() < 0.5:
        # Horizontal oval
        radius_x = min(width, height) // 2 * random.uniform(0.7, 0.95)
        radius_y = radius_x / aspect_ratio
    else:
        # Vertical oval
        radius_y = min(width, height) // 2 * random.uniform(0.7, 0.95)
        radius_x = radius_y / aspect_ratio
    
    # Create points around the oval
    num_points = random.randint(12, 24)
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    
    # Add random variations to the radius
    points = []
    for i in range(num_points):
        angle = angles[i]
        # Base oval equation
        r_oval = (radius_x * radius_y) / np.sqrt((radius_y * np.cos(angle))**2 + (radius_x * np.sin(angle))**2)
        # Add irregularity
        r = r_oval * (1 + irregularity * (random.random() - 0.5))
        
        x = center_x + int(r * np.cos(angle))
        y = center_y + int(r * np.sin(angle))
        points.append([x, y])
    
    # Create mask
    mask = np.zeros((height, width), dtype=np.uint8)
    points_array = np.array(points, dtype=np.int32)
    cv2.fillPoly(mask, [points_array], 255)
    
    return mask

def create_crescent_mask(width, height):
    """
    Create a crescent (half-moon) shaped mask
    """
    center_x = width // 2
    center_y = height // 2
    radius = min(width, height) // 2 * random.uniform(0.7, 0.95)
    
    # Create the full circle mask
    mask1 = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask1, (center_x, center_y), int(radius), 255, -1)
    
    # Create the second circle that will be subtracted
    offset_x = random.randint(-int(radius * 0.6), int(radius * 0.6))
    offset_y = random.randint(-int(radius * 0.6), int(radius * 0.6))
    second_radius = int(radius * random.uniform(0.7, 0.9))
    
    mask2 = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask2, (center_x + offset_x, center_y + offset_y), second_radius, 255, -1)
    
    # Subtract the second circle from the first
    crescent_mask = cv2.subtract(mask1, mask2)
    
    return crescent_mask

def create_random_segment_mask(width, height):
    """
    Create a completely random segment mask
    """
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # Create a few random points
    num_points = random.randint(5, 12)
    points = []
    
    for _ in range(num_points):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        points.append([x, y])
    
    # Close the polygon by ensuring it's convex
    points = np.array(points, dtype=np.int32)
    hull = cv2.convexHull(points)
    
    # Fill the polygon
    cv2.fillPoly(mask, [hull], 255)
    
    return mask

def create_segmentation_mask(width, height):
    """
    Create a random segmentation mask with distribution favoring irregular circles
    """
    # Probability distribution for different shapes
    prob = random.random()
    
    if prob < 0.6:
        # 60% chance of irregular circle
        mask = create_irregular_circle_mask(width, height)
    elif prob < 0.8:
        # 20% chance of irregular oval
        mask = create_irregular_oval_mask(width, height)
    elif prob < 0.9:
        # 10% chance of crescent
        mask = create_crescent_mask(width, height)
    else:
        # 10% chance of random segment
        mask = create_random_segment_mask(width, height)
    
    # Make the edges pixelated/jagged
    # Apply a series of erosions and dilations with different structuring elements
    for _ in range(random.randint(1, 3)):
        # Create a random structuring element
        size = random.choice([3, 5])
        struct = np.ones((size, size), dtype=np.uint8)
        
        # Add random holes to the structuring element
        for i in range(size):
            for j in range(size):
                if random.random() < 0.3:
                    struct[i, j] = 0
        
        if random.random() < 0.5:
            mask = binary_erosion(mask, structure=struct).astype(np.uint8) * 255
        else:
            mask = binary_dilation(mask, structure=struct).astype(np.uint8) * 255
    
    return mask

def apply_mask_to_image(image, mask):
    """
    Apply the mask to the image, creating a transparent background
    """
    # Convert grayscale to RGB if needed
    if len(image.shape) == 2:  # Grayscale image
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    # Ensure the image has an alpha channel
    if image.shape[2] == 3:  # RGB image
        alpha = np.ones((image.shape[0], image.shape[1], 1), dtype=np.uint8) * 255
        image_with_alpha = np.concatenate([image, alpha], axis=2)
    else:  # Already has alpha channel
        image_with_alpha = image.copy()
    
    # Apply the mask to the alpha channel
    image_with_alpha[:, :, 3] = mask
    
    return image_with_alpha

def process_images(config):
    """
    Process images according to the configuration
    """
    src_imgs = config['src_imgs']
    dst_cropp = config['dst_cropp']
    num_crops_per_image = config['numbCropp_PerImage']
    min_size = config['min_size']
    max_size = config['max_size']
    
    # Create output directory
    create_output_dir(dst_cropp)
    
    # Get all image files
    img_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    
    for ext in img_extensions:
        image_files.extend(list(Path(src_imgs).glob(f'*{ext}')))
        image_files.extend(list(Path(src_imgs).glob(f'*{ext.upper()}')))
    
    if not image_files:
        print(f"No image files found in {src_imgs}")
        return
    
    print(f"Found {len(image_files)} image files")
    
    total_crops = 0
    failed_crops = 0
    
    # Process each image
    for img_path in tqdm(image_files, desc="Processing images"):
        try:
            # Load the image
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"Failed to load image: {img_path}")
                continue
            
            # Check if image is grayscale (2D) and convert to RGB if needed
            if len(img.shape) == 2:  # If grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:  # If RGBA
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            elif img.shape[2] == 3:  # If BGR
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Generate crops for this image
            for crop_idx in range(num_crops_per_image):
                # Get a random crop
                crop = random_crop(img, min_size, max_size)
                if crop is None:
                    failed_crops += 1
                    continue
                
                # Create a segmentation mask for the crop
                mask = create_segmentation_mask(crop.shape[1], crop.shape[0])
                
                # Apply the mask to the crop
                masked_crop = apply_mask_to_image(crop, mask)
                
                # Save the masked crop
                output_file = f"{img_path.stem}_crop{crop_idx}.png"
                output_path = os.path.join(dst_cropp, output_file)
                
                # Save as PNG to preserve transparency
                cv2.imwrite(output_path, cv2.cvtColor(masked_crop, cv2.COLOR_RGBA2BGRA))
                
                total_crops += 1
                
                # Print progress every 1000 crops
                if total_crops % 1000 == 0:
                    print(f"Generated {total_crops} crops so far...")
        
        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")
            continue
    
    print(f"Processing complete. Generated {total_crops} crops.")
    if failed_crops > 0:
        print(f"Failed to create {failed_crops} crops due to size constraints.")

def main():
    path_config = "config.yaml"
    
    # Load configuration
    config = load_config(path_config)
    
    # Process images
    process_images(config)

if __name__ == "__main__":
    main()