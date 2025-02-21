import cv2
import numpy as np
import os
from pathlib import Path
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def extract_largest_segment(image_path, output_path):
    """
    Извлекает наибольший сегмент из изображения и сохраняет результат
    
    Args:
        image_path (Path): путь к исходному изображению
        output_path (Path): путь для сохранения результата
    
    Returns:
        bool: True если обработка успешна, False в случае ошибки
    """
    try:
        # Читаем изображение
        image = cv2.imread(str(image_path))
        if image is None:
            logging.error(f"Не удалось прочитать изображение: {image_path}")
            return False
        
        # Преобразуем в градации серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Применяем размытие по Гауссу для уменьшения шума
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Применяем пороговую обработку
        _, binary = cv2.threshold(blurred, 250, 255, cv2.THRESH_BINARY_INV)
        
        # Применяем морфологические операции
        kernel = np.ones((5,5), np.uint8)
        # Закрытие (closing) помогает заполнить маленькие отверстия
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        # Открытие (opening) убирает мелкий шум
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Находим контуры
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logging.warning(f"Не найдены сегменты в изображении: {image_path}")
            return False
        
        # Фильтруем контуры по минимальной площади
        min_area = 100  # Можно настроить это значение
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        if not valid_contours:
            logging.warning(f"Не найдены сегменты подходящего размера: {image_path}")
            return False
        
        # Находим наибольший контур
        largest_contour = max(valid_contours, key=cv2.contourArea)
        
        # Получаем ограничивающий прямоугольник
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Создаем маску для сегмента
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [largest_contour], -1, (255), -1)
        
        # Применяем маску к исходному изображению
        result = image.copy()
        result[mask == 0] = [255, 255, 255]
        
        # Добавляем отступы при вырезании сегмента
        padding = 10
        y1 = max(0, y - padding)
        y2 = min(image.shape[0], y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(image.shape[1], x + w + padding)
        
        # Вырезаем сегмент с отступами
        segment = result[y1:y2, x1:x2]
        
        # Сохраняем результат
        cv2.imwrite(str(output_path), segment)
        logging.info(f"Успешно обработано: {image_path}")
        return True
        
    except Exception as e:
        logging.error(f"Ошибка при обработке {image_path}: {str(e)}")
        return False

def process_directory(src_path, dst_path):
    """
    Обрабатывает все изображения в указанной директории
    
    Args:
        src_path (str): путь к директории с исходными изображениями
        dst_path (str): путь к директории для сохранения результатов
    """
    # Преобразуем пути в объекты Path
    src_dir = Path(src_path)
    dst_dir = Path(dst_path)
    
    # Создаем директорию назначения, если она не существует
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    # Список поддерживаемых расширений
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    
    # Счетчики для статистики
    total_files = 0
    successful_files = 0
    
    # Обрабатываем все файлы в директории
    for image_path in src_dir.iterdir():
        if image_path.suffix.lower() in image_extensions:
            total_files += 1
            output_path = dst_dir / f"processed_{image_path.name}"
            
            if extract_largest_segment(image_path, output_path):
                successful_files += 1
    
    # Выводим итоговую статистику
    logging.info(f"Обработка завершена. Успешно обработано {successful_files} из {total_files} файлов")

def main():
    # Пути к директориям (можно заменить на аргументы командной строки)
    src_path = "/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/003_tomatos/003_tomatoes_ripeness_stage/001_raw_data/003_001_Dima_Yaroslav_20_11_24_TkPodmoskovie_video/003_unverified_annotation/001_prepare_data_Gelya_18_02_25/not_cropped/Part3"
    dst_path = "/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/003_tomatos/003_tomatoes_ripeness_stage/001_raw_data/003_001_Dima_Yaroslav_20_11_24_TkPodmoskovie_video/003_unverified_annotation/001_prepare_data_Gelya_18_02_25/cropped_centr/Part3"
    
    try:
        process_directory(src_path, dst_path)
    except Exception as e:
        logging.error(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()