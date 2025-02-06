import os
import yaml
import subprocess
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path='config.yaml'):
    """Загрузка и проверка конфигурации"""
    try:
        logging.info(f"Пытаемся загрузить конфигурацию из {os.path.abspath(config_path)}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Проверка наличия необходимых ключей
        required_keys = ['src_yolo', 'dst_LabelStudio']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"В конфигурации отсутствуют обязательные ключи: {missing_keys}")
            
        return config
    except FileNotFoundError:
        logging.error(f"Файл конфигурации не найден: {os.path.abspath(config_path)}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Ошибка парсинга YAML: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Неожиданная ошибка при загрузке конфигурации: {str(e)}")
        raise

def verify_paths(config):
    """Проверка существования путей и их доступности"""
    # Проверка src_yolo
    src_path = Path(config['src_yolo'])
    logging.info(f"Проверка пути источника: {src_path.absolute()}")
    
    if not src_path.exists():
        logging.error(f"Путь источника не существует: {src_path.absolute()}")
        logging.info("Проверьте:")
        logging.info("1. Правильность пути в config.yaml")
        logging.info("2. Подключен ли внешний диск")
        logging.info("3. Права доступа к директории")
        raise FileNotFoundError(f"Путь источника не найден: {src_path.absolute()}")
    
    if not src_path.is_dir():
        logging.error(f"Путь источника не является директорией: {src_path.absolute()}")
        raise NotADirectoryError(f"Путь источника не является директорией: {src_path.absolute()}")
    
    # Проверка dst_LabelStudio
    dst_path = Path(config['dst_LabelStudio'])
    logging.info(f"Проверка пути назначения: {dst_path.absolute()}")
    
    # Пробуем создать выходную директорию
    try:
        dst_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Выходная директория создана/существует: {dst_path.absolute()}")
    except Exception as e:
        logging.error(f"Не удалось создать выходную директорию: {str(e)}")
        raise

def convert_datasets(src_yolo, dst_LabelStudio):
    """Конвертация датасетов"""
    # Получаем список директорий
    try:
        directories = [d for d in os.listdir(src_yolo) if os.path.isdir(os.path.join(src_yolo, d))]
        logging.info(f"Найдено директорий для обработки: {len(directories)}")
        
        if not directories:
            logging.warning("Не найдено поддиректорий для обработки!")
            return
        
        for inside_name in directories:
            full_path_inside_name = os.path.join(src_yolo, inside_name)
            dst_path = os.path.join(dst_LabelStudio, inside_name)
            variable_bash_dst_json = os.path.join(dst_LabelStudio, inside_name, f"{inside_name}.json")
            
            # Создаем выходную директорию
            os.makedirs(dst_path, exist_ok=True)
            logging.info(f"Обработка директории: {inside_name}")
            
            # Формируем команду
            command = f'label-studio-converter import yolo -i {full_path_inside_name} -o {variable_bash_dst_json} --image-root-url "/data/local-files/?d={inside_name}/images"'
            
            logging.info(f"Выполняем команду: {command}")
            
            try:
                result = subprocess.run(command, shell=True, check=True, 
                                     capture_output=True, text=True)
                logging.info(f"Успешно сконвертировано: {inside_name}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Ошибка конвертации {inside_name}:")
                logging.error(f"Код ошибки: {e.returncode}")
                logging.error(f"Вывод: {e.output}")
                logging.error(f"Ошибка: {e.stderr}")
    except Exception as e:
        logging.error(f"Ошибка при получении списка директорий: {str(e)}")
        raise

def main():
    try:
        # Загружаем конфигурацию
        config = load_config()
        
        # Проверяем пути
        verify_paths(config)
        
        # Запускаем конвертацию
        convert_datasets(config['src_yolo'], config['dst_LabelStudio'])
        
        logging.info("Конвертация успешно завершена")
        
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()