import os
import yaml
from PIL import Image
from pathlib import Path

def load_config(config_path):
    """
    Загрузка конфигурации из YAML файла
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def process_images(src_dir, dst_dir, angle):
    """
    Рекурсивная обработка изображений во всех подпапках
    """
    # Создаем корневую папку назначения, если она не существует
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    
    # Поддерживаемые форматы изображений
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    
    # Рекурсивный обход всех папок
    for root, dirs, files in os.walk(src_dir):
        # Создаем соответствующую структуру папок в dst_dir
        rel_path = os.path.relpath(root, src_dir)
        current_dst_dir = os.path.join(dst_dir, rel_path)
        Path(current_dst_dir).mkdir(parents=True, exist_ok=True)
        
        # Обрабатываем все файлы в текущей папке
        for file in files:
            # Проверяем расширение файла
            if any(file.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                try:
                    # Полные пути к файлам
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(current_dst_dir, file)
                    
                    # Открываем и поворачиваем изображение
                    with Image.open(src_path) as img:
                        # Поворачиваем изображение
                        rotated_img = img.rotate(-angle, expand=True)  # Отрицательный угол для поворота по часовой стрелке
                        
                        # Сохраняем изображение
                        rotated_img.save(dst_path, quality=100, subsampling=0)
                        
                    print(f"Обработано: {src_path} -> {dst_path}")
                    
                except Exception as e:
                    print(f"Ошибка при обработке {src_path}: {str(e)}")

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
        
        # Обрабатываем изображения
        process_images(
            src_dir=config['src'],
            dst_dir=config['dst'],
            angle=config['angle']
        )
        
        print("Обработка завершена успешно!")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()