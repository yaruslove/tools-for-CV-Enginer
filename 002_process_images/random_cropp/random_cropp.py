import cv2
import numpy as np
import os
from pathlib import Path
import random
import time
from concurrent.futures import ThreadPoolExecutor

def random_crop_images(path_in, path_out, n_crops, max_size, min_size):
    """
    Создает случайные кропы изображений из указанной директории
    
    Args:
        path_in (str): Путь к директории с исходными изображениями
        path_out (str): Путь для сохранения кропов
        n_crops (int): Количество кропов
        max_size (int): Максимальный размер стороны кропа
        min_size (int): Минимальный размер стороны кропа
    """
    
    # Создаем директорию для выходных изображений если её нет
    Path(path_out).mkdir(parents=True, exist_ok=True)
    
    # Получаем список всех изображений
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP']
    image_paths = [
        f for f in Path(path_in).glob('**/*') 
        if f.suffix.lower() in valid_extensions
    ]
    
    if not image_paths:
        raise ValueError(f"Не найдены изображения в {path_in}")

    def process_single_crop(i):
        # Выбираем случайное изображение
        img_path = random.choice(image_paths)
        
        # Читаем изображение
        img = cv2.imread(str(img_path))
        if img is None:
            return
        
        h, w = img.shape[:2]
        
        # Определяем случайные размеры кропа
        crop_w = random.randint(min_size, min(max_size, w))
        crop_h = random.randint(min_size, min(max_size, h))
        
        # Определяем случайную позицию кропа
        x = random.randint(0, w - crop_w)
        y = random.randint(0, h - crop_h)
        
        # Делаем кроп
        crop = img[y:y+crop_h, x:x+crop_w]
        
        # Создаем уникальное имя файла используя timestamp и случайное число
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        filename = f"crop_{timestamp}_{random_suffix}.jpg"
        output_path = os.path.join(path_out, filename)
        
        # Сохраняем кроп
        cv2.imwrite(output_path, crop)

    # Используем ThreadPoolExecutor для параллельной обработки
    with ThreadPoolExecutor() as executor:
        list(executor.map(process_single_crop, range(n_crops)))

# Пример использования
if __name__ == "__main__":
    random_crop_images(
        path_in="/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/001_leaves_diseases/002_quality_classifier/001_raw_data/002_034_ImageNet_val_garbage/002_raw_data_img/ILSVRC2012_img_val",
        path_out="/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/001_leaves_diseases/002_quality_classifier/001_raw_data/002_034_ImageNet_val_garbage/005_verified_annotation/002_random_cropp_16_01_25_train/7",
        n_crops=5000,
        max_size=210,
        min_size=55
    )