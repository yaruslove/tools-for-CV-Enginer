import os
import cv2
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import Optional, Dict

def extract_frames_ffmpeg(video_path: str, output_dir: str, frame_rate: int, base_name: str, 
                         hw_params: dict = None) -> None:
    try:
        output_pattern = os.path.join(output_dir, f"{base_name}_%d.jpg")
        
        # Улучшенная конфигурация FFmpeg
        stream = ffmpeg.input(video_path, vsync=0)  # Добавляем vsync=0
        
        if hw_params:
            stream = ffmpeg.input(video_path, **hw_params, vsync=0)
        
        # Оптимизируем параметры
        stream = stream.filter('fps', fps=1/frame_rate)
        stream = stream.output(output_pattern,
                             format='image2',
                             vcodec='mjpeg',
                             qscale=2,  # Уменьшаем качество для скорости
                             threads=multiprocessing.cpu_count())  # Используем все ядра
        
        # Добавляем параметры overwrite и loglevel
        ffmpeg.run(stream, 
                  overwrite_output=True,
                  capture_stdout=True,
                  capture_stderr=True,
                  cmd=['ffmpeg', '-loglevel', 'error'])  # Уменьшаем вывод логов
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return None



def grab_frame_optimized(src_loc: str, dst_loc: str, rate_loc: int, 
                        base_name_file: str, hw_accel: Optional[str] = None,
                        use_ffmpeg: bool = True) -> None:
    
    if use_ffmpeg:
        try:
            hw_params = {
                'hwaccel': 'auto',  # Автоматический выбор ускорения
                'hwaccel_device': '0'
            }
            extract_frames_ffmpeg(src_loc, dst_loc, rate_loc, base_name_file, hw_params)
            return
        except Exception as e:
            print(f"FFmpeg failed, falling back to OpenCV: {e}")
    
    # Оптимизация для OpenCV
    cap_params = {'buffersize': 10240}  # Увеличиваем буфер
    
    if hw_accel == 'cuda':
        cap_params['apiPreference'] = cv2.CAP_CUDA
    elif hw_accel == 'videotoolbox':
        cap_params['apiPreference'] = cv2.CAP_VIDEOTOOLBOX
    elif hw_accel == 'intel':
        cap_params['apiPreference'] = cv2.CAP_INTEL_MFX
    elif hw_accel == 'amd':
        cap_params['apiPreference'] = cv2.CAP_VIDEOPROCESS_AMD
    
    video = cv2.VideoCapture(src_loc, **cap_params)
    if not video.isOpened():
        print(f"Error opening video: {src_loc}")
        return
    
    # Оптимизация чтения кадров
    video.set(cv2.CAP_PROP_BUFFERSIZE, 1024)
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_extract = range(0, total_frames, rate_loc)
    
    # Оптимизация записи изображений
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # Уменьшаем качество для скорости
    
    def process_frame(frame_idx):
        video.set(1, frame_idx)
        ret, frame = video.read()
        if ret:
            name_out = os.path.join(dst_loc, f"{base_name_file}_{frame_idx//rate_loc}.jpg")
            cv2.imwrite(name_out, frame, encode_params)
    
    # Увеличиваем количество потоков
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 2) as executor:
        list(executor.map(process_frame, frames_to_extract))
    
    video.release()