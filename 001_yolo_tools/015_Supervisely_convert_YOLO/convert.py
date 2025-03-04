import os
import json
import yaml
import re
from tqdm import tqdm

def get_class_ids(json_dir):
    """
    Extract all unique class titles from JSON files and assign them numeric IDs for YOLO format.
    
    Args:
        json_dir (str): Directory containing JSON annotation files
        
    Returns:
        dict: Dictionary mapping class titles to YOLO class IDs
    """
    class_titles = set()
    
    # Get list of JSON files in source directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    # Extract all unique class titles
    for filename in json_files:
        file_path = os.path.join(json_dir, filename)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for obj in data.get('objects', []):
                class_title = obj.get('classTitle', '')
                if class_title:
                    class_titles.add(class_title)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Sort class titles alphabetically and assign IDs
    sorted_classes = sorted(class_titles)
    class_map = {class_title: idx for idx, class_title in enumerate(sorted_classes)}
    
    return class_map

def convert_to_yolo_format(json_dir, yolo_dir, class_map):
    """
    Convert JSON annotations to YOLO format.
    
    Args:
        json_dir (str): Directory containing JSON annotation files
        yolo_dir (str): Directory to save YOLO format annotation files
        class_map (dict): Dictionary mapping class titles to YOLO class IDs
        
    Returns:
        int: Number of files processed
    """
    # Create destination directory if it doesn't exist
    os.makedirs(yolo_dir, exist_ok=True)
    
    # Get list of JSON files in source directory
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {json_dir}")
        return 0
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process files with progress bar
    count = 0
    for filename in tqdm(json_files, desc="Converting annotations"):
        src_path = os.path.join(json_dir, filename)
        
        try:
            # Load JSON data
            with open(src_path, 'r') as f:
                data = json.load(f)
            
            # Extract base name for the YOLO file
            # Pattern: match anything before .jpg.json or similar
            pattern = r'(.+?)(\.(jpg|jpeg|png|bmp|gif))\.json$'
            match = re.match(pattern, filename, re.IGNORECASE)
            
            if match:
                base_name = match.group(1)
            else:
                # If no match, just use the filename without .json
                base_name = os.path.splitext(filename)[0]
            
            # Create YOLO format filename
            yolo_filename = f"{base_name}.txt"
            dst_path = os.path.join(yolo_dir, yolo_filename)
            
            # Extract image dimensions
            img_width = data.get('size', {}).get('width', 0)
            img_height = data.get('size', {}).get('height', 0)
            
            if img_width <= 0 or img_height <= 0:
                print(f"Warning: Invalid image dimensions in {filename}, skipping")
                continue
            
            # Process objects and convert to YOLO format
            yolo_annotations = []
            for obj in data.get('objects', []):
                class_title = obj.get('classTitle', '')
                geometry_type = obj.get('geometryType', '')
                
                # Skip if class title is not found or geometry is not rectangle
                if not class_title or geometry_type != 'rectangle':
                    continue
                
                # Get class ID
                class_id = class_map.get(class_title)
                if class_id is None:
                    print(f"Warning: Unknown class {class_title} in {filename}, skipping")
                    continue
                
                # Extract bounding box coordinates
                points = obj.get('points', {})
                exterior = points.get('exterior', [])
                
                if len(exterior) != 2:
                    print(f"Warning: Invalid rectangle format in {filename}, skipping object")
                    continue
                
                # Extract coordinates
                x_min, y_min = exterior[0]
                x_max, y_max = exterior[1]
                
                # Convert to YOLO format:
                # <class> <x_center> <y_center> <width> <height>
                # where x, y, width, height are relative to image size
                
                x_center = (x_min + x_max) / 2.0 / img_width
                y_center = (y_min + y_max) / 2.0 / img_height
                bbox_width = (x_max - x_min) / img_width
                bbox_height = (y_max - y_min) / img_height
                
                # Create YOLO format line
                yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}"
                yolo_annotations.append(yolo_line)
            
            # Save YOLO annotations to file
            with open(dst_path, 'w') as f:
                f.write('\n'.join(yolo_annotations))
            
            count += 1
            
            # Show some examples for verification
            if count <= 3:  # Show first 3 examples
                print(f"Converted: {filename} -> {yolo_filename}")
                print(f"  Sample annotations: {yolo_annotations[:2]}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    return count

def create_classes_file(class_map, dst_dir):
    """
    Create a classes.txt file mapping class IDs to class names.
    
    Args:
        class_map (dict): Dictionary mapping class titles to YOLO class IDs
        dst_dir (str): Directory to save the classes file
    """
    classes_path = os.path.join(dst_dir, 'classes.txt')
    
    # Invert the class map for writing
    id_to_class = {id: name for name, id in class_map.items()}
    
    # Write class names in order of class ID
    with open(classes_path, 'w') as f:
        for class_id in range(len(class_map)):
            class_name = id_to_class.get(class_id, f"unknown_{class_id}")
            f.write(f"{class_name}\n")
    
    print(f"Classes file created at {classes_path}")
    # Print class mapping for reference
    print("Class mapping:")
    for name, id in sorted(class_map.items(), key=lambda x: x[1]):
        print(f"  {id}: {name}")

def main():
    """Main function to run the converter."""
    # Read configuration from YAML file
    config_path = "config.yaml"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found!")
        print("Creating a sample configuration file...")
        
        # Create a sample configuration file
        sample_config = {
            'src': '/path/to/json_files',
            'dst': '/path/to/yolo_files'
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
    src_dir = config.get('src')
    dst_dir = config.get('dst')
    
    # Validate configuration
    if not src_dir or not dst_dir:
        print("Error: Missing required parameters in configuration file.")
        print("Make sure 'src' and 'dst' are defined.")
        return
    
    # Check if directories exist
    if not os.path.exists(src_dir):
        print(f"Error: Source directory {src_dir} does not exist!")
        return
    
    # Create a class mapping
    print("Analyzing JSON files to extract classes...")
    class_map = get_class_ids(src_dir)
    
    if not class_map:
        print("Error: No classes found in JSON files.")
        return
    
    print(f"Found {len(class_map)} classes.")
    
    # Create classes file
    create_classes_file(class_map, dst_dir)
    
    # Process the files
    count = convert_to_yolo_format(src_dir, dst_dir, class_map)
    
    print(f"\nConversion complete. {count} files processed.")
    print(f"YOLO format annotations saved to: {dst_dir}")

if __name__ == "__main__":
    main()