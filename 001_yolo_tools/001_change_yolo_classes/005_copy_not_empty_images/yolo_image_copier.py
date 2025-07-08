import os
import yaml
import shutil
import glob
from pathlib import Path

def load_config(config_path="config.yaml"):
    assert os.path.exists(config_path), f"Файл конфигурации {config_path} не найден!"
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    assert all(key in config for key in ['src_labels', 'src_images', 'dst_images']), \
        "Отсутствуют обязательные параметры в конфигурации"
    return config

def get_non_empty_prefixes(labels_path):
    assert os.path.exists(labels_path), f"Директория с лейблами не найдена: {labels_path}"
    
    prefixes = []
    for txt_file in glob.glob(os.path.join(labels_path, "*.txt")):
        if os.path.getsize(txt_file) > 0:
            with open(txt_file, 'r', encoding='utf-8') as f:
                if f.read().strip():
                    prefixes.append(Path(txt_file).stem)
    
    assert prefixes, "Не найдено непустых файлов лейблов"
    print(f"Найдено непустых лейблов: {len(prefixes)}")
    return prefixes

def copy_images(prefixes, src_path, dst_path):
    assert os.path.exists(src_path), f"Директория с изображениями не найдена: {src_path}"
    os.makedirs(dst_path, exist_ok=True)
    
    extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    copied = 0
    
    for prefix in prefixes:
        for ext in extensions:
            pattern = os.path.join(src_path, f"{prefix}.{ext}")
            for image_path in glob.glob(pattern):
                shutil.copy2(image_path, dst_path)
                copied += 1
                print(f"Скопировано: {Path(image_path).name}")
    
    print(f"Всего скопировано: {copied}")

def main():
    config = load_config()
    prefixes = get_non_empty_prefixes(config['src_labels'])
    copy_images(prefixes, config['src_images'], config['dst_images'])
    print("Завершено!")

if __name__ == "__main__":
    main()