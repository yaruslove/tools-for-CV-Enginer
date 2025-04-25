#!/usr/bin/env python3
import yaml
import glob
import os
from tqdm import tqdm

# Захардкоженный путь к конфигурационному файлу
config_path = "config.yaml"

def remap_yolo_annotations(config_path):
    # Загрузка YAML конфигурации
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Проверка структуры конфига
    assert 'was' in config, "Config must contain 'was' field"
    assert 'remap' in config, "Config must contain 'remap' field"
    assert 'src_annot_dir' in config, "Config must contain 'src_annot_dir' field"
    assert 'dst_annot_dir' in config, "Config must contain 'dst_annot_dir' field"
    assert 'dst_classes' in config, "Config must contain 'dst_classes' field"
    
    # Получение путей к директориям и файлам
    src_annot_dir = config['src_annot_dir']
    dst_annot_dir = config['dst_annot_dir']
    dst_classes_path = config['dst_classes']
    
    # Проверка существования исходной директории
    assert os.path.exists(src_annot_dir), f"Source directory '{src_annot_dir}' does not exist"
    
    # Создание директории назначения, если она не существует
    os.makedirs(dst_annot_dir, exist_ok=True)
    
    # Создание директории для файла классов, если она не существует
    dst_classes_dir = os.path.dirname(dst_classes_path)
    if dst_classes_dir:
        os.makedirs(dst_classes_dir, exist_ok=True)
    
    # Получение списка старых классов и словаря ремаппинга
    was_classes = config['was']
    remap_dict = config['remap']
    
    # Создание мэппинга от старых class_id к новым class_id
    class_id_mapping = {}
    for new_class_id, (new_class_name, old_class_name) in enumerate(remap_dict.items()):
        if old_class_name != "none":
            assert old_class_name in was_classes, f"Class '{old_class_name}' not found in 'was' list"
            old_class_id = was_classes.index(old_class_name)
            class_id_mapping[old_class_id] = new_class_id
    
    # Сохранение новых классов в файл
    new_classes = list(remap_dict.keys())
    with open(dst_classes_path, 'w') as f:
        f.write('\n'.join(new_classes))
    
    print(f"Classes saved to {dst_classes_path}")
    
    # Получение списка всех TXT файлов
    annotation_files = glob.glob(os.path.join(src_annot_dir, "*.txt"))
    
    # Обработка всех TXT файлов в исходной директории с прогресс-баром
    for src_annot_file in tqdm(annotation_files, desc="Processing annotations"):
        # Получаем имя файла для сохранения в директории назначения
        file_name = os.path.basename(src_annot_file)
        dst_annot_file = os.path.join(dst_annot_dir, file_name)
        
        with open(src_annot_file, 'r') as file:
            lines = file.readlines()
        
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if not parts:  # Пропускаем пустые строки
                continue
            
            assert len(parts) == 5, f"Invalid format in {src_annot_file}: expected 5 values per line"
            assert parts[0].isdigit(), f"Invalid class_id in {src_annot_file}: '{parts[0]}' is not an integer"
            
            old_class_id = int(parts[0])
            
            if old_class_id in class_id_mapping:
                parts[0] = str(class_id_mapping[old_class_id])
            
            updated_lines.append(" ".join(parts))
        
        # Записываем обновленное содержимое в файл назначения
        with open(dst_annot_file, 'w') as file:
            if updated_lines:
                file.write("\n".join(updated_lines) + "\n")
    
    total_files = len(annotation_files)
    print(f"\nProcess completed successfully!")
    print(f"Total processed files: {total_files}")
    print(f"Source directory: {src_annot_dir}")
    print(f"Destination directory: {dst_annot_dir}")
    print(f"Classes file: {dst_classes_path}")

def main():
    remap_yolo_annotations(config_path)

if __name__ == "__main__":
    main()

