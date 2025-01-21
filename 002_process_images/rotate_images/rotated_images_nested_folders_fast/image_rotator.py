import os
import yaml
from PIL import Image
from pathlib import Path
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm
import time

def load_config(config_path):
    """
    Загрузка конфигурации из YAML файла
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def process_single_image(args):
    """
    Обработка одного изображения
    """
    src_path, dst_path, angle = args
    try:
        # Создаем родительскую директорию если её нет
        Path(os.path.dirname(dst_path)).mkdir(parents=True, exist_ok=True)
        
        # Открываем и поворачиваем изображение
        with Image.open(src_path) as img:
            # Оптимизация: проверяем, нужно ли поворачивать
            if angle % 360 != 0:
                rotated_img = img.rotate(-angle, expand=True)  # Отрицательный угол для поворота по часовой стрелке
                rotated_img.save(dst_path, quality=95, subsampling=0)
            else:
                img.save(dst_path, quality=95, subsampling=0)
                
        return True, src_path
    except Exception as e:
        return False, f"Ошибка при обработке {src_path}: {str(e)}"

def collect_image_files(src_dir):
    """
    Собирает все изображения для обработки
    """
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    image_files = []
    
    for root, _, files in os.walk(src_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                src_path = os.path.join(root, file)
                image_files.append(src_path)
    
    return image_files

def prepare_tasks(src_dir, dst_dir, image_files, angle):
    """
    Подготовка списка задач для параллельной обработки
    """
    tasks = []
    for src_path in image_files:
        # Создаем соответствующий путь в dst_dir
        rel_path = os.path.relpath(src_path, src_dir)
        dst_path = os.path.join(dst_dir, rel_path)
        tasks.append((src_path, dst_path, angle))
    return tasks

def process_images_parallel(src_dir, dst_dir, angle, num_processes=None):
    """
    Параллельная обработка изображений
    """
    # Создаем корневую папку назначения
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    
    # Собираем все файлы для обработки
    print("Сканирование директорий...")
    image_files = collect_image_files(src_dir)
    total_files = len(image_files)
    
    if total_files == 0:
        print("Изображения не найдены!")
        return
    
    print(f"Найдено {total_files} изображений")
    
    # Подготавливаем задачи
    tasks = prepare_tasks(src_dir, dst_dir, image_files, angle)
    
    # Определяем количество процессов
    if num_processes is None:
        num_processes = min(cpu_count(), 8)  # Используем максимум 8 процессов
    
    # Запускаем параллельную обработку
    print(f"Запуск обработки на {num_processes} процессах...")
    start_time = time.time()
    
    with Pool(num_processes) as pool:
        results = list(tqdm(
            pool.imap(process_single_image, tasks),
            total=len(tasks),
            desc="Обработка изображений"
        ))
    
    # Анализ результатов
    successful = sum(1 for success, _ in results if success)
    failed = [(msg) for success, msg in results if not success]
    
    # Вывод статистики
    end_time = time.time()
    duration = end_time - start_time
    
    print("\nСтатистика обработки:")
    print(f"Всего обработано: {total_files}")
    print(f"Успешно: {successful}")
    print(f"С ошибками: {len(failed)}")
    print(f"Время обработки: {duration:.2f} секунд")
    print(f"Среднее время на файл: {(duration/total_files):.3f} секунд")
    
    # Вывод ошибок, если есть
    if failed:
        print("\nСписок ошибок:")
        for error in failed:
            print(error)

def main():
    # Путь к конфигурационному файлу
    config_path = 'config.yaml'
    
    try:
        # Загружаем конфигурацию
        config = load_config(config_path)
        
        # Проверяем наличие необходимых параметров
        required_params = ['src', 'dst', 'angle']
        if not all(param in config for param in required_params):
            raise ValueError("В конфигурационном файле отсутствуют необходимые параметры")
        
        # Получаем количество процессов из конфига или используем значение по умолчанию
        num_processes = config.get('num_processes', None)
        
        # Обрабатываем изображения
        process_images_parallel(
            src_dir=config['src'],
            dst_dir=config['dst'],
            angle=config['angle'],
            num_processes=num_processes
        )
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()