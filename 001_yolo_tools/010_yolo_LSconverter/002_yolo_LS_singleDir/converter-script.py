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
        logging.info(f"Загрузка конфигурации из {os.path.abspath(config_path)}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
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

def verify_paths(config):
    """Проверка существования путей и их доступности"""
    src_path = Path(config['src_yolo'])
    logging.info(f"Проверка пути источника: {src_path.absolute()}")
    
    # Проверка наличия подпапок images и labels
    if not (src_path / 'images').exists() or not (src_path / 'labels').exists():
        logging.error(f"В директории источника отсутствует папка images или labels: {src_path.absolute()}")
        logging.info("Структура директории должна быть:")
        logging.info("src_yolo/")
        logging.info("    ├── images/")
        logging.info("    └── labels/")
        raise FileNotFoundError("Неверная структура директории источника")

    # Проверка dst_LabelStudio
    dst_path = Path(config['dst_LabelStudio'])
    logging.info(f"Проверка пути назначения: {dst_path.absolute()}")
    
    try:
        dst_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Выходная директория создана/существует: {dst_path.absolute()}")
    except Exception as e:
        logging.error(f"Не удалось создать выходную директорию: {str(e)}")
        raise

def convert_dataset(src_yolo, dst_LabelStudio):
    """Конвертация датасета"""
    try:
        # Формируем пути
        dataset_name = os.path.basename(src_yolo)
        output_json = os.path.join(dst_LabelStudio, f"{dataset_name}.json")
        
        # Формируем команду конвертации
        command = f'label-studio-converter import yolo -i {src_yolo} -o {output_json} --image-root-url "/data/local-files/?d=images"'
        
        logging.info(f"Выполнение команды: {command}")
        
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        logging.info("Конвертация успешно завершена")
        
    except subprocess.CalledProcessError as e:
        logging.error("Ошибка при конвертации:")
        logging.error(f"Код ошибки: {e.returncode}")
        logging.error(f"Вывод: {e.output}")
        logging.error(f"Ошибка: {e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Неожиданная ошибка при конвертации: {str(e)}")
        raise

def main():
    try:
        config = load_config()
        verify_paths(config)
        convert_dataset(config['src_yolo'], config['dst_LabelStudio'])
        logging.info("Процесс успешно завершен")
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()