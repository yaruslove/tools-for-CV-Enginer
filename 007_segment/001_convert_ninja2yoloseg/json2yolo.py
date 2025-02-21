import os
import json
import yaml
from collections import defaultdict

def convert_json_to_yolo_segmentation(json_path, output_dir):
    """
    Convert a JSON annotation file to YOLO segmentation format
    
    Args:
        json_path (str): Path to the JSON file
        output_dir (str): Directory to save the YOLO txt file
    
    Returns:
        set: Set of class titles found in this JSON file
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get image dimensions
    img_height = data['size']['height']
    img_width = data['size']['width']
    
    # Create a dictionary to store class titles and their IDs
    class_title_to_id = {}
    class_titles = set()
    
    # Create the output filename (same as input but with .txt extension)
    base_filename = os.path.basename(json_path)
    base_name = os.path.splitext(base_filename)[0]
    txt_filename = os.path.join(output_dir, f"{base_name}.txt")
    
    with open(txt_filename, 'w') as out_file:
        for obj in data['objects']:
            class_title = obj['classTitle']
            class_titles.add(class_title)
            
            # Get the polygon points
            exterior_points = obj['points']['exterior']
            
            # Normalize coordinates and format as required by YOLO
            yolo_line = [class_title]  # Temporarily use class title instead of index
            
            for point in exterior_points:
                x, y = point
                # Normalize coordinates to [0, 1]
                x_norm = x / img_width
                y_norm = y / img_height
                
                yolo_line.extend([f"{x_norm:.6f}", f"{y_norm:.6f}"])
            
            # Write the line to the output file
            out_file.write(' '.join(yolo_line) + '\n')
    
    return class_titles

def create_classes_file(all_class_titles, output_dir):
    """
    Create a classes.txt file with all unique class titles
    
    Args:
        all_class_titles (list): List of all unique class titles
        output_dir (str): Directory to save the classes.txt file
    """
    # Sort class titles to ensure consistent ordering
    sorted_classes = sorted(all_class_titles)
    
    # Create a classes.txt file with all unique class titles
    classes_path = os.path.join(output_dir, 'classes.txt')
    with open(classes_path, 'w') as f:
        for class_title in sorted_classes:
            f.write(f"{class_title}\n")
    
    return sorted_classes

def update_class_indices(output_dir, class_title_to_idx):
    """
    Update all text files with class indices instead of class titles
    
    Args:
        output_dir (str): Directory containing the text files
        class_title_to_idx (dict): Mapping from class titles to indices
    """
    for filename in os.listdir(output_dir):
        if filename.endswith('.txt') and filename != 'classes.txt':
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Update class indices
            updated_lines = []
            for line in lines:
                parts = line.strip().split(' ')
                class_title = parts[0]
                class_idx = class_title_to_idx[class_title]
                updated_line = f"{class_idx} {' '.join(parts[1:])}"
                updated_lines.append(updated_line)
            
            # Write updated contents back
            with open(file_path, 'w') as f:
                f.write('\n'.join(updated_lines))

def main():
    # Read configuration from YAML file
    config_path = "config.yaml"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found!")
        print("Creating a sample configuration file...")
        
        # Create a sample configuration file
        sample_config = {
            'src_json': '/path/to/json_files',
            'out_path': '/path/to/output_directory'
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
    src_json = config.get('src_json')
    out_path = config.get('out_path')
    
    # Validate configuration
    if not src_json or not out_path:
        print("Error: Missing required parameters in configuration file.")
        print("Make sure 'src_json' and 'out_path' are defined.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(out_path, exist_ok=True)
    
    # Process all JSON files
    all_class_titles = set()
    json_files = [f for f in os.listdir(src_json) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {src_json}")
        return
    
    print(f"Processing {len(json_files)} JSON files...")
    
    for filename in json_files:
        json_path = os.path.join(src_json, filename)
        class_titles = convert_json_to_yolo_segmentation(json_path, out_path)
        all_class_titles.update(class_titles)
    
    # Create classes.txt file and get the sorted classes
    sorted_classes = create_classes_file(all_class_titles, out_path)
    
    # Create a mapping from class titles to indices
    class_title_to_idx = {title: idx for idx, title in enumerate(sorted_classes)}
    
    # Update all text files with class indices
    update_class_indices(out_path, class_title_to_idx)
    
    print(f"Conversion complete. {len(json_files)} files processed.")
    print(f"Classes found: {sorted_classes}")
    print(f"Output saved to: {out_path}")

if __name__ == "__main__":
    main()