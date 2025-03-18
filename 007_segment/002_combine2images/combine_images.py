#!/usr/bin/env python3
import os
import yaml
from pathlib import Path
from PIL import Image

# Путь до конфига (захардкожен)
CONFIG_PATH = "config.yaml"

def load_config(config_path):
    """Загрузка конфигурации из YAML файла."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        # Проверка наличия всех необходимых параметров
        required_params = ['src1', 'src2', 'dst']
        for param in required_params:
            if param not in config:
                raise ValueError(f"В конфиге отсутствует параметр: {param}")
        return config
    except Exception as e:
        print(f"Ошибка при загрузке конфига: {e}")
        exit(1)

def merge_images(img1_path, img2_path, output_path):
    """Склеивает две фотографии горизонтально и сохраняет результат.
    Размер холста определяется по большей картинке. Вторая картинка 
    масштабируется для заполнения своей половины холста, сохраняя пропорции."""
    try:
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        
        # Определяем размеры большей картинки
        img1_area = img1.width * img1.height
        img2_area = img2.width * img2.height
        
        if img1_area >= img2_area:
            base_width = img1.width
            base_height = img1.height
        else:
            base_width = img2.width
            base_height = img2.height
        
        # Создаем холст в два раза шире большей картинки
        canvas_width = base_width * 2
        canvas_height = base_height
        merged_img = Image.new('RGB', (canvas_width, canvas_height))
        
        # Масштабируем первую картинку, если нужно
        if img1.width != base_width or img1.height != base_height:
            # Сохраняем пропорции, масштабируя до заполнения левой половины
            ratio = min(base_width / img1.width, base_height / img1.height)
            new_width = int(img1.width * ratio)
            new_height = int(img1.height * ratio)
            img1_resized = img1.resize((new_width, new_height), Image.LANCZOS)
            
            # Вычисляем позицию для центрирования изображения
            left_pos = (base_width - new_width) // 2
            top_pos = (base_height - new_height) // 2
            
            # Вставляем первое изображение
            merged_img.paste(img1_resized, (left_pos, top_pos))
        else:
            # Вставляем первую картинку без изменений
            merged_img.paste(img1, (0, 0))
        
        # Масштабируем вторую картинку, чтобы она заполнила правую половину
        # Сохраняем соотношение сторон, вписывая в доступное пространство
        ratio = min(base_width / img2.width, base_height / img2.height)
        new_width = int(img2.width * ratio)
        new_height = int(img2.height * ratio)
        img2_resized = img2.resize((new_width, new_height), Image.LANCZOS)
        
        # Вычисляем позицию для центрирования изображения в правой половине
        right_half_start = base_width
        left_pos = right_half_start + (base_width - new_width) // 2
        top_pos = (base_height - new_height) // 2
        
        # Вставляем второе изображение
        merged_img.paste(img2_resized, (left_pos, top_pos))
        
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Сохраняем результат
        merged_img.save(output_path)
        print(f"Сохранено: {output_path}")
        return True
    except Exception as e:
        print(f"Ошибка при обработке {img1_path} и {img2_path}: {e}")
        return False

def process_folders(src1, src2, dst_path):
    """Обрабатывает файлы в указанных папках."""
    # Проверка существования директорий
    if not os.path.isdir(src1):
        print(f"Ошибка: директория {src1} не существует")
        return
    if not os.path.isdir(src2):
        print(f"Ошибка: директория {src2} не существует")
        return
    
    # Создаем папку назначения, если её нет
    os.makedirs(dst_path, exist_ok=True)
    
    # Получаем список файлов в первой папке
    src1_files = os.listdir(src1)
    processed_count = 0
    error_count = 0
    
    for filename in src1_files:
        # Проверяем, является ли файл изображением
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Проверяем, существует ли файл с таким же именем во второй папке
            src1_file_path = os.path.join(src1, filename)
            src2_file_path = os.path.join(src2, filename)
            
            if os.path.exists(src2_file_path):
                # Формируем путь для сохранения результата
                dst_file_path = os.path.join(dst_path, filename)
                
                # Склеиваем изображения
                success = merge_images(src1_file_path, src2_file_path, dst_file_path)
                
                if success:
                    processed_count += 1
                else:
                    error_count += 1
            else:
                print(f"Пропуск: {filename} не найден в {src2}")
    
    print(f"\nОбработка завершена:")
    print(f"Всего обработано: {processed_count} пар изображений")
    print(f"Ошибок: {error_count}")

def main():
    """Основная функция скрипта."""
    print("Запуск скрипта для склеивания изображений...")
    
    # Загрузка конфигурации
    config = load_config(CONFIG_PATH)
    
    # Выводим информацию о настройках
    print(f"Исходная папка 1: {config['src1']}")
    print(f"Исходная папка 2: {config['src2']}")
    print(f"Папка для результатов: {config['dst']}")
    
    # Обработка папок
    process_folders(config['src1'], config['src2'], config['dst'])

if __name__ == "__main__":
    main()