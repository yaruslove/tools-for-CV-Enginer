import os
import shutil
import yaml
from pathlib import Path
from typing import List, Tuple

def load_config(config_path: str = "config.yaml") -> dict:
    """Загружает конфигурацию из YAML файла"""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def get_image_label_pairs(src_data: str) -> List[Tuple[str, str, int]]:
    """
    Получает пары изображение-лейбл с размером файла лейбла
    Возвращает список кортежей (image_path, label_path, label_size)
    """
    images_dir = Path(src_data) / "images"
    labels_dir = Path(src_data) / "labels"
    
    pairs = []
    
    # Получаем все файлы изображений
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    for img_file in images_dir.iterdir():
        if img_file.suffix.lower() in image_extensions:
            # Ищем соответствующий файл лейбла
            label_file = labels_dir / f"{img_file.stem}.txt"
            
            if label_file.exists():
                label_size = label_file.stat().st_size
                pairs.append((str(img_file), str(label_file), label_size))
    
    return pairs

def sort_pairs_by_label_size(pairs: List[Tuple[str, str, int]]) -> List[Tuple[str, str, int]]:
    """Сортирует пары по размеру файла лейбла (по убыванию)"""
    return sorted(pairs, key=lambda x: x[2], reverse=True)

def create_directories(dst_data: str):
    """Создает необходимые директории"""
    dst_path = Path(dst_data)
    
    # Создаем основные директории
    train_dir = dst_path / "train"
    val_dir = dst_path / "val"
    
    # Создаем поддиректории для images и labels
    for split_dir in [train_dir, val_dir]:
        (split_dir / "images").mkdir(parents=True, exist_ok=True)
        (split_dir / "labels").mkdir(parents=True, exist_ok=True)

def copy_files(pairs: List[Tuple[str, str, int]], dst_data: str, split: str, count: int):
    """Копирует файлы в соответствующие директории"""
    dst_path = Path(dst_data) / split
    
    for i, (img_path, label_path, _) in enumerate(pairs[:count]):
        # Копируем изображение
        img_filename = Path(img_path).name
        shutil.copy2(img_path, dst_path / "images" / img_filename)
        
        # Копируем лейбл
        label_filename = Path(label_path).name
        shutil.copy2(label_path, dst_path / "labels" / label_filename)
        
        print(f"Copied {split} {i+1}/{count}: {img_filename}")

def split_dataset():
    """Основная функция для разбивки датасета"""
    # Загружаем конфигурацию
    config = load_config()
    
    src_data = config['src_data']
    dst_data = config['dst_data']
    train_count = config['train']
    val_count = config['val']
    
    print(f"Source data: {src_data}")
    print(f"Destination data: {dst_data}")
    print(f"Train samples: {train_count}")
    print(f"Val samples: {val_count}")
    
    # Проверяем существование исходных директорий
    src_path = Path(src_data)
    if not (src_path / "images").exists() or not (src_path / "labels").exists():
        raise FileNotFoundError(f"Images or labels directory not found in {src_data}")
    
    # Получаем пары изображение-лейбл
    print("Collecting image-label pairs...")
    pairs = get_image_label_pairs(src_data)
    print(f"Found {len(pairs)} pairs")
    
    # Проверяем, достаточно ли данных
    total_needed = train_count + val_count
    if len(pairs) < total_needed:
        raise ValueError(f"Not enough data! Found {len(pairs)} pairs, but need {total_needed}")
    
    # Сортируем по размеру файлов лейблов (по убыванию)
    print("Sorting by label file size...")
    sorted_pairs = sort_pairs_by_label_size(pairs)
    
    # Показываем статистику по размерам
    print("\nTop 5 largest label files:")
    for i, (img_path, label_path, size) in enumerate(sorted_pairs[:5]):
        print(f"{i+1}. {Path(label_path).name}: {size} bytes")
    
    # Создаем директории
    print("Creating directories...")
    create_directories(dst_data)
    
    # Копируем файлы для train
    print(f"\nCopying {train_count} samples to train...")
    train_pairs = sorted_pairs[:train_count]
    copy_files(train_pairs, dst_data, "train", train_count)
    
    # Копируем файлы для val
    print(f"\nCopying {val_count} samples to val...")
    val_pairs = sorted_pairs[train_count:train_count + val_count]
    copy_files(val_pairs, dst_data, "val", val_count)
    
    print(f"\nDataset splitting completed!")
    print(f"Train: {train_count} samples")
    print(f"Val: {val_count} samples")
    print(f"Total: {train_count + val_count} samples")

if __name__ == "__main__":
    try:
        split_dataset()
    except Exception as e:
        print(f"Error: {e}")
