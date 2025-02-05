import os
import ffmpeg
from ffmpeg._run import Error as FFmpegError
import yaml
from pathlib import Path
from typing import Dict, Any
from tqdm import tqdm

def load_config(config_path: str) -> Dict[str, Any]:
    """Загрузка конфигурации из YAML файла"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def grab_frame(src_loc: str, dst_loc: str, rate_loc: int, base_name_file: str) -> None:
    """
    Извлекает кадры из видео используя ffmpeg
    
    Args:
        src_loc: путь к исходному видео
        dst_loc: путь для сохранения кадров
        rate_loc: частота извлечения кадров
        base_name_file: базовое имя для сохраняемых кадров
    """
    try:
        output_pattern = os.path.join(dst_loc, f"{base_name_file}_%d.jpg")
        
        # Создаем команду ffmpeg
        stream = ffmpeg.input(src_loc)
        stream = stream.filter('fps', fps=1/rate_loc)  # Устанавливаем частоту кадров
        stream = stream.output(
            output_pattern,
            format='image2',
            vcodec='mjpeg',
            qscale=1
        )
        
        # Запускаем ffmpeg
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        
    except FFmpegError as e:
        print(f"FFmpeg error processing {src_loc}:")
        if hasattr(e, 'stderr'):
            print(e.stderr.decode())
        else:
            print(str(e))
    except Exception as e:
        print(f"Unexpected error processing {src_loc}: {str(e)}")

def main():
    try:
        # Загружаем конфигурацию
        config = load_config('config.yaml')
        
        src_path = config['input']['src']
        dst_path = config['input']['dst']
        rate = config['input']['rate']
        
        # Проверяем существование исходной директории
        if not os.path.exists(src_path):
            raise ValueError(f"Source path does not exist: {src_path}")
        
        # Создаем выходную директорию если её нет
        os.makedirs(dst_path, exist_ok=True)
        
        # Обработка одного файла
        if os.path.isfile(src_path):
            base_name_file = Path(src_path).stem
            print(f"Processing single file: {base_name_file}")
            grab_frame(src_path, dst_path, rate, base_name_file)
            return
        
        # Обработка директории с видео
        if os.path.isdir(src_path):
            vid_formats = tuple(config['video_formats'])
            files_to_process = [
                file_path for file_path in Path(src_path).iterdir()
                if file_path.suffix.lower() in vid_formats and not file_path.name.startswith('.')
            ]
            
            if not files_to_process:
                print(f"No video files found in {src_path}")
                return
            
            print(f"Found {len(files_to_process)} video files to process")
            
            # Обрабатываем файлы с прогресс-баром
            for file_path in tqdm(files_to_process, desc="Processing videos"):
                base_name_file = file_path.stem
                dst_loc = os.path.join(dst_path, base_name_file)
                
                # Создаем поддиректорию для кадров текущего видео
                os.makedirs(dst_loc, exist_ok=True)
                
                try:
                    grab_frame(str(file_path), dst_loc, rate, base_name_file)
                except Exception as e:
                    print(f"\nError processing {file_path.name}: {str(e)}")
                    continue
    
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        exit(1)