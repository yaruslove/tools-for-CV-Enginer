import os
import yaml
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from tabulate import tabulate
from natsort import natsorted
from PIL import Image

def get_image_stats(directory):
    """
    Подсчитывает количество изображений в указанной директории
    и вычисляет средний размер (ширину и высоту) этих изображений.
    
    Возвращает:
    - Количество изображений
    - Средний размер (ширина, высота)
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    count = 0
    width_sum = 0
    height_sum = 0
    
    assert os.path.exists(directory), f"Директория {directory} не существует"
    assert os.path.isdir(directory), f"{directory} не является директорией"
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in image_extensions:
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        width_sum += width
                        height_sum += height
                        count += 1
                except Exception as e:
                    print(f"Ошибка при чтении изображения {file_path}: {e}")
                    continue
    
    if count > 0:
        avg_width = round(width_sum / count)
        avg_height = round(height_sum / count)
        return count, (avg_width, avg_height)
    else:
        return 0, (0, 0)

def main():
    # Загрузка конфигурации из YAML
    assert os.path.exists('config.yaml'), "Файл конфигурации config.yaml не найден"
    
    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    # Извлечение параметров из конфигурации
    src_dir = config.get('src')
    dst_csv = config.get('dst_csv')
    orientation = config.get('orientation', 'vertical')  # По умолчанию вертикальное расположение
    
    assert src_dir is not None, "В конфигурационном файле отсутствует параметр 'src'"
    assert dst_csv is not None, "В конфигурационном файле отсутствует параметр 'dst_csv'"
    assert orientation in ['vertical', 'horizontal'], "Параметр 'orientation' должен быть 'vertical' или 'horizontal'"
    assert os.path.exists(src_dir), f"Директория источника {src_dir} не существует"
    assert os.path.isdir(src_dir), f"{src_dir} не является директорией"
    
    # Создание директории для CSV файла, если она не существует
    csv_dir = os.path.dirname(dst_csv)
    if csv_dir and not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    
    # Сбор данных о количестве и размерах изображений в каждой директории
    class_stats = {}
    all_images_count = 0
    all_width_sum = 0
    all_height_sum = 0
    
    # Получение списка директорий и их естественная сортировка
    dirs = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    sorted_dirs = natsorted(dirs)
    
    for class_dir in sorted_dirs:
        class_path = os.path.join(src_dir, class_dir)
        count, (avg_width, avg_height) = get_image_stats(class_path)
        class_stats[class_dir] = {
            'count': count,
            'avg_size': f"{avg_width}x{avg_height}"
        }
        
        # Накапливаем статистику для всего датасета
        all_images_count += count
        all_width_sum += avg_width * count
        all_height_sum += avg_height * count
    
    assert class_stats, "Не найдено классов с изображениями в указанной директории"
    
    # Вычисляем средний размер для всего датасета
    if all_images_count > 0:
        avg_width_all = round(all_width_sum / all_images_count)
        avg_height_all = round(all_height_sum / all_images_count)
        total_avg_size = f"{avg_width_all}x{avg_height_all}"
    else:
        total_avg_size = "0x0"
    
    # Сохранение результатов в CSV файл
    with open(dst_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['class', 'count', 'avg_size'])
        for class_name, stats in class_stats.items():
            writer.writerow([class_name, stats['count'], stats['avg_size']])
        writer.writerow(['Total', all_images_count, total_avg_size])
    
    print(f"Результаты сохранены в {dst_csv}")
    
    # Вывод результатов в терминал в виде таблицы
    if orientation == 'vertical':
        # Вертикальное отображение (классы в строках)
        rows = []
        for class_name, stats in class_stats.items():
            rows.append([class_name, stats['count'], stats['avg_size']])
        
        # Добавление итоговой строки
        rows.append(['Total', all_images_count, total_avg_size])
        
        # Создаем DataFrame и выводим таблицу
        df = pd.DataFrame(rows, columns=['class', 'count', 'avg_size'])
        
        print("\nСтатистика по классам (вертикальное отображение):")
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        # Горизонтальное отображение (классы в столбцах)
        # Создаем два словаря: один для количества, другой для средних размеров
        counts_data = {}
        sizes_data = {}
        
        for class_name, stats in class_stats.items():
            counts_data[class_name] = stats['count']
            sizes_data[class_name] = stats['avg_size']
        
        # Добавляем total
        counts_data['total'] = all_images_count
        sizes_data['total'] = total_avg_size
        
        # Создаем DataFrame с двумя строками
        df = pd.DataFrame([counts_data, sizes_data])
        df.index = ['count', 'avg_size']
        
        # Вывод таблицы
        print("\nСтатистика по классам (горизонтальное отображение):")
        print(tabulate(df, headers='keys', tablefmt='fancy_grid'))

if __name__ == "__main__":
    main()