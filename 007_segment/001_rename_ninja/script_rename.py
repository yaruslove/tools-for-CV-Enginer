import os
import shutil
import yaml
import re
from tqdm import tqdm

def rename_and_copy_files(src_dir, dst_dir):
    """
    Copy files from src_dir to dst_dir while renaming them:
    IMG_1232.jpg.json -> IMG_1232.json
    IMG_1232.jpg.txt -> IMG_1232.txt
    
    Args:
        src_dir (str): Source directory containing the files
        dst_dir (str): Destination directory for renamed files
    
    Returns:
        int: Number of files processed
    """
    # Create destination directory if it doesn't exist
    os.makedirs(dst_dir, exist_ok=True)
    
    # Get list of JSON and TXT files in source directory
    target_files = [f for f in os.listdir(src_dir) if f.endswith('.json') or f.endswith('.txt')]
    
    if not target_files:
        print(f"No JSON or TXT files found in {src_dir}")
        return 0
    
    print(f"Found {len(target_files)} JSON/TXT files to process")
    
    # Process files with progress bar
    count = 0
    for filename in tqdm(target_files, desc="Processing files"):
        src_path = os.path.join(src_dir, filename)
        
        # Determine file extension (json or txt)
        file_ext = os.path.splitext(filename)[1]  # Gets .json or .txt
        
        # Extract the base name by removing the image extension before .json or .txt
        # Pattern: match anything that ends with an image extension followed by .json or .txt
        pattern = r'(.+?)(\.(jpg|jpeg|png|bmp|gif))(\.json|\.txt)$'
        match = re.match(pattern, filename, re.IGNORECASE)
        
        if match:
            # Get the base name (without image extension) and the file extension (json or txt)
            base_name = match.group(1)
            file_extension = os.path.splitext(filename)[1]  # Gets .json or .txt
            new_filename = f"{base_name}{file_extension}"
            dst_path = os.path.join(dst_dir, new_filename)
            
            # Copy and rename the file
            shutil.copy2(src_path, dst_path)
            count += 1
            
            # Show some examples for verification
            if count <= 3:  # Show first 3 examples
                print(f"Renamed: {filename} -> {new_filename}")
        else:
            # File already has the correct naming pattern or doesn't match expected pattern
            print(f"Skipping (no pattern match): {filename}")
    
    return count

def main():
    """Main function to run the program."""
    # Read configuration from YAML file
    config_path = "rename_config.yaml"
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file {config_path} not found!")
        print("Creating a sample configuration file...")
        
        # Create a sample configuration file
        sample_config = {
            'src': '/path/to/source_files',
            'dst': '/path/to/destination_files'
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
    
    # Process the files
    count = rename_and_copy_files(src_dir, dst_dir)
    
    print(f"\nRenaming complete. {count} files processed.")
    print(f"Renamed files saved to: {dst_dir}")

if __name__ == "__main__":
    main()