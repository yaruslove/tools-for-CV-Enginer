import os
import shutil
import random
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def load_config(config_path: str) -> Dict:
    """
    Загрузка конфигурации из YAML файла
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def create_directory_structure(dst_path: str) -> Tuple[str, str]:
    """
    Создание структуры директорий train и val
    """
    train_path = os.path.join(dst_path, 'train')
    val_path = os.path.join(dst_path, 'val')
    
    os.makedirs(train_path, exist_ok=True)
    os.makedirs(val_path, exist_ok=True)
    
    return train_path, val_path

def get_class_files(class_path: str) -> List[str]:
    """
    Получение списка файлов изображений из директории класса
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    return [f for f in os.listdir(class_path) 
            if os.path.splitext(f)[1].lower() in valid_extensions]

def split_and_copy_files(src_class_path: str, 
                        train_class_path: str,
                        val_class_path: str,
                        files: List[str],
                        train_percent: float) -> None:
    """
    Разделение и копирование файлов в train и val директории
    """
    # Определяем количество файлов для train
    num_files = len(files)
    num_train = int(num_files * train_percent / 100)
    
    # Случайно перемешиваем файлы
    random.shuffle(files)
    
    # Разделяем на train и val
    train_files = files[:num_train]
    val_files = files[num_train:]
    
    # Создаем директории для классов
    os.makedirs(train_class_path, exist_ok=True)
    os.makedirs(val_class_path, exist_ok=True)
    
    # Копируем файлы
    for f in train_files:
        shutil.copy2(
            os.path.join(src_class_path, f),
            os.path.join(train_class_path, f)
        )
    
    for f in val_files:
        shutil.copy2(
            os.path.join(src_class_path, f),
            os.path.join(val_class_path, f)
        )

def main(config_path: str):
    """
    Основная функция скрипта
    """
    # Загружаем конфигурацию
    config = load_config(config_path)
    
    src_path = config['src_path']
    dst_path = config['dst_path']
    train_percent = config['train_percent']
    
    # Проверяем входные данные
    if not os.path.exists(src_path):
        raise ValueError(f"Source path {src_path} does not exist")
    
    if train_percent < 0 or train_percent > 100:
        raise ValueError(f"Train percent must be between 0 and 100")
    
    # Создаем структуру директорий
    train_path, val_path = create_directory_structure(dst_path)
    
    # Обрабатываем каждый класс
    for class_name in os.listdir(src_path):
        src_class_path = os.path.join(src_path, class_name)
        
        # Пропускаем файлы, обрабатываем только директории
        if not os.path.isdir(src_class_path):
            continue
            
        # Создаем пути для train и val директорий класса
        train_class_path = os.path.join(train_path, class_name)
        val_class_path = os.path.join(val_path, class_name)
        
        # Получаем список файлов
        files = get_class_files(src_class_path)
        
        if not files:
            print(f"Warning: No valid images found in {src_class_path}")
            continue
            
        # Разделяем и копируем файлы
        split_and_copy_files(
            src_class_path,
            train_class_path,
            val_class_path,
            files,
            train_percent
        )
        
        print(f"Processed class {class_name}")

if __name__ == "__main__":

   path_config = "config.yaml"
   main(path_config)