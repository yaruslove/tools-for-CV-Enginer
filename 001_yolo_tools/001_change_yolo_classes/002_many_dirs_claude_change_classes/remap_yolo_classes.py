import os
import yaml
import shutil
from pathlib import Path
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            logging.info(f"Loaded configuration from {config_path}")
            return config
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        raise

def validate_config(config: dict) -> None:
    """
    Validate configuration parameters
    """
    required_params = ['src_labels', 'dst_labels', 'rematch_classes']
    
    # Check required parameters
    for param in required_params:
        if param not in config:
            raise ValueError(f"Missing required parameter: {param}")
    
    # Check paths
    if not os.path.exists(config['src_labels']):
        raise FileNotFoundError(f"Source directory not found: {config['src_labels']}")
    
    # Validate rematch_classes format
    if not isinstance(config['rematch_classes'], dict):
        raise ValueError("rematch_classes must be a dictionary")
    
    try:
        # Convert string keys to integers if needed
        config['rematch_classes'] = {int(k): int(v) for k, v in config['rematch_classes'].items()}
    except ValueError:
        raise ValueError("All keys and values in rematch_classes must be integers")

def process_label_file(src_file: str, dst_file: str, class_mapping: dict) -> None:
    """
    Process single label file
    """
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        
        # Process empty files
        if os.path.getsize(src_file) == 0:
            shutil.copy2(src_file, dst_file)
            return
        
        with open(src_file, 'r') as f:
            lines = f.read().strip().split('\n')
        
        new_lines = []
        for line in lines:
            parts = line.strip().split(' ')
            if not parts:  # Skip empty lines
                continue
                
            try:
                class_id = int(parts[0])
                # Replace class if it's in mapping
                if class_id in class_mapping:
                    parts[0] = str(class_mapping[class_id])
                new_lines.append(' '.join(parts))
            except (ValueError, IndexError) as e:
                logging.warning(f"Invalid line in {src_file}: {line}")
                continue
        
        # Write processed lines
        with open(dst_file, 'w') as f:
            f.write('\n'.join(new_lines))
            
    except Exception as e:
        logging.error(f"Error processing {src_file}: {str(e)}")
        raise

def process_directory(config: dict) -> None:
    """
    Process all label files in the directory
    """
    try:
        src_path = Path(config['src_labels'])
        dst_path = Path(config['dst_labels'])
        
        # Create destination directory
        dst_path.mkdir(parents=True, exist_ok=True)
        
        # Get all txt files recursively
        label_files = list(src_path.rglob('*.txt'))
        logging.info(f"Found {len(label_files)} label files")
        
        # Process each file
        for src_file in tqdm(label_files, desc="Processing labels"):
            # Create corresponding destination path
            rel_path = src_file.relative_to(src_path)
            dst_file = dst_path / rel_path
            
            process_label_file(
                str(src_file),
                str(dst_file),
                config['rematch_classes']
            )
            
        logging.info("Processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        raise

def main():
    try:
        # Load and validate configuration
        config = load_config('config.yaml')
        validate_config(config)
        
        # Process files
        process_directory(config)
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()