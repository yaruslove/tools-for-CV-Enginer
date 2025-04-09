import os
import cv2
import yaml
import textwrap
import argparse
import tqdm
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import platform
from typing import Dict, Any
from pathlib import Path
from frame_processing import grab_frame_optimized

def detect_hardware_acceleration():
    """Определяет доступное аппаратное ускорение"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        try:
            test_cap = cv2.VideoCapture()
            if hasattr(cv2, 'CAP_VIDEOTOOLBOX'):
                return 'videotoolbox'
        except:
            pass
    
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        return 'cuda'
    
    try:
        if hasattr(cv2, 'CAP_VIDEOPROCESS_AMD'):
            return 'amd'
        if hasattr(cv2, 'CAP_AMF'):
            return 'amf'
    except:
        pass
    
    try:
        if cv2.videoio_registry.getBackendName(cv2.CAP_INTEL_MFX) is not None:
            return 'intel'
    except:
        pass
    
    return 'cpu'

def load_config(config_path: str) -> Dict[str, Any]:
    """Загрузка конфигурации из YAML файла"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config.setdefault('hardware', {}).setdefault('force_cpu', False)
    config.setdefault('processing', {}).setdefault('max_workers', None)
    config.setdefault('processing', {}).setdefault('use_ffmpeg', True)
    config.setdefault('video_formats', ['.mp4', '.avi', '.MOV', '.asf'])
    
    return config

def validate_config(config: Dict[str, Any]) -> None:
    """Проверка конфигурации"""
    required_fields = ['input.src', 'input.dst', 'input.rate']
    
    for field in required_fields:
        parts = field.split('.')
        current = config
        for part in parts:
            if part not in current:
                raise ValueError(f"Missing required field: {field}")
            current = current[part]
    
    if not os.path.exists(config['input']['src']):
        raise ValueError(f"Source path does not exist: {config['input']['src']}")
    
    os.makedirs(config['input']['dst'], exist_ok=True)

def process_video(args):
    """Обработка одного видео"""
    src_loc, dst_loc, rate, base_name_file, hw_accel, use_ffmpeg = args
    grab_frame_optimized(src_loc, dst_loc, rate, base_name_file, hw_accel, use_ffmpeg)

def main():

    yaml_config = 'config.yaml'
    
    config = load_config(yaml_config) # args.config
    validate_config(config)
    
    hw_accel = None if config['hardware']['force_cpu'] else detect_hardware_acceleration()
    print(f"Using hardware acceleration: {hw_accel}")
    
    src_path = config['input']['src']
    dst_path = config['input']['dst']
    rate = config['input']['rate']
    max_workers = config['processing']['max_workers'] or multiprocessing.cpu_count()
    
    if os.path.isfile(src_path):
        base_name_file = Path(src_path).stem
        grab_frame_optimized(
            src_path, 
            dst_path, 
            rate, 
            base_name_file, 
            hw_accel,
            use_ffmpeg=config['processing']['use_ffmpeg']
        )
    
    elif os.path.isdir(src_path):
        video_files = []
        vid_formats = tuple('.' + fmt.lower().lstrip('.') for fmt in config['video_formats'])
        
        for file_path in Path(src_path).iterdir():
            if file_path.suffix.lower() in vid_formats and not file_path.name.startswith('.'):
                src_loc = str(file_path)
                base_name_file = file_path.stem
                dst_loc = os.path.join(dst_path, base_name_file)
                
                os.makedirs(dst_loc, exist_ok=True)
                
                video_files.append((
                    src_loc,
                    dst_loc,
                    rate,
                    base_name_file,
                    hw_accel,
                    config['processing']['use_ffmpeg']
                ))
            else:
                print(f"Skipping file: {file_path}")
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            list(tqdm.tqdm(
                executor.map(process_video, video_files),
                total=len(video_files)
            ))

if __name__ == '__main__':
    main()
