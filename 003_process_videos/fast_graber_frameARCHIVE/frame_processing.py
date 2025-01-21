import os
import cv2
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import Optional, Dict

def extract_frames_ffmpeg(video_path: str, output_dir: str, frame_rate: int, base_name: str, 
                         hw_params: dict = None) -> None:
    """Извлекает кадры используя ffmpeg с поддержкой аппаратного ускорения"""
    try:
        output_pattern = os.path.join(output_dir, f"{base_name}_%d.jpg")
        
        # Базовая конфигурация
        stream = ffmpeg.input(video_path)
        
        # Добавляем параметры аппаратного ускорения
        if hw_params:
            stream = ffmpeg.input(video_path, **hw_params)
        
        stream = stream.filter('fps', fps=1/frame_rate)
        stream = stream.output(output_pattern, format='image2', vcodec='mjpeg', qscale=1)
        
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return None

def grab_frame_optimized(src_loc: str, dst_loc: str, rate_loc: int, 
                        base_name_file: str, hw_accel: Optional[str] = None,
                        use_ffmpeg: bool = True) -> None:
    """Оптимизированная функция захвата кадров с поддержкой аппаратного ускорения"""
    
    # Пробуем сначала использовать FFmpeg, если разрешено
    if use_ffmpeg:
        try:
            # Добавляем поддержку AMD для FFmpeg
            hw_params = {}
            if hw_accel == 'amd' or hw_accel == 'amf':
                hw_params = {
                    'hwaccel': 'amf',
                    'hwaccel_device': '0'
                }
            extract_frames_ffmpeg(src_loc, dst_loc, rate_loc, base_name_file, hw_params)
            return
        except Exception as e:
            print(f"FFmpeg failed, falling back to OpenCV: {e}")
    
    # Настройка параметров захвата видео
    cap_params = {}
    if hw_accel == 'cuda':
        cap_params['apiPreference'] = cv2.CAP_CUDA
    elif hw_accel == 'videotoolbox':
        cap_params['apiPreference'] = cv2.CAP_VIDEOTOOLBOX
    elif hw_accel == 'intel':
        cap_params['apiPreference'] = cv2.CAP_INTEL_MFX
    elif hw_accel == 'amd':
        cap_params['apiPreference'] = cv2.CAP_VIDEOPROCESS_AMD
    elif hw_accel == 'amf':
        cap_params['apiPreference'] = cv2.CAP_AMF
    
    # Оптимизация для AMD
    if hw_accel in ['amd', 'amf']:
        try:
            cv2.ocl.setUseOpenCL(True)
            if cv2.ocl.haveOpenCL():
                print("Using OpenCL acceleration for AMD GPU")
        except:
            print("OpenCL acceleration not available")
    
    video = cv2.VideoCapture(src_loc, **cap_params)
    
    if not video.isOpened():
        print(f"Error opening video: {src_loc}")
        return
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_extract = range(0, total_frames, rate_loc)
    
    def process_frame(frame_idx):
        video.set(1, frame_idx)
        ret, frame = video.read()
        if ret:
            if hw_accel in ['amd', 'amf'] and cv2.ocl.haveOpenCL():
                frame = cv2.UMat(frame)
            
            name_out = os.path.join(dst_loc, f"{base_name_file}_{frame_idx//rate_loc}.jpg")
            cv2.imwrite(name_out, frame)
    
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        list(executor.map(process_frame, frames_to_extract))
    
    video.release()