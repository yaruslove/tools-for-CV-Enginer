import os
import yaml
import csv
import pandas as pd
from pathlib import Path
from tabulate import tabulate
from natsort import natsorted

def count_images_in_directory(directory):
    """
    Подсчитывает количество изображений в указанной директории.
    Изображениями считаются файлы с расширениями jpg, jpeg, png, gif, bmp.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    count = 0
    
    assert os.path.exists(directory), f"Директория {directory} не существует"
    assert os.path.isdir(directory), f"{directory} не является директорией"
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in image_extensions:
                count += 1
    
    return count

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
    
    # Сбор данных о количестве изображений в каждой директории
    image_counts = {}
    
    # Получение списка директорий и их естественная сортировка
    dirs = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    sorted_dirs = natsorted(dirs)
    
    for class_dir in sorted_dirs:
        class_path = os.path.join(src_dir, class_dir)
        count = count_images_in_directory(class_path)
        image_counts[class_dir] = count
    
    assert image_counts, "Не найдено классов с изображениями в указанной директории"
    
    # Сохранение результатов в CSV файл
    with open(dst_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['class', 'count'])
        for class_name, count in image_counts.items():
            writer.writerow([class_name, count])
    
    print(f"Результаты сохранены в {dst_csv}")
    
    # Вывод результатов в терминал в виде таблицы
    if orientation == 'vertical':
        # Вертикальное отображение (классы в строках)
        df = pd.DataFrame(list(image_counts.items()), columns=['class', 'count'])
        
        # Добавление итоговой строки
        total_images = sum(image_counts.values())
        total_row = pd.DataFrame([['Total', total_images]], columns=['class', 'count'])
        df = pd.concat([df, total_row])
        
        # Вывод таблицы
        print("\nСтатистика по классам (вертикальное отображение):")
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        # Горизонтальное отображение (классы в столбцах)
        # Создаем словарь с данными классов и добавляем total в конец
        display_data = image_counts.copy()
        display_data['total'] = sum(image_counts.values())
        
        # Создаем DataFrame с одной строкой
        df = pd.DataFrame([display_data])
        df.index = ['count']
        
        # Вывод таблицы
        print("\nСтатистика по классам (горизонтальное отображение):")
        print(tabulate(df, headers='keys', tablefmt='fancy_grid'))

if __name__ == "__main__":
    main()