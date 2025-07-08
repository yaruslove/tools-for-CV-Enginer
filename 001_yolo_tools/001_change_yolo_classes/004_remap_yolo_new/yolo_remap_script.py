import yaml
import os
from pathlib import Path


def load_config(config_path):
    """Загружает конфигурацию из YAML файла"""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def create_class_mapping(as_is_classes, remap, order_new_classes):
    """
    Создает маппинг от старых индексов классов к новым
    
    Args:
        as_is_classes: список текущих классов
        remap: словарь ремаппинга старое_имя -> новое_имя
        order_new_classes: список новых классов в нужном порядке
    
    Returns:
        dict: маппинг старый_индекс -> новый_индекс
    """
    # Создаем словарь старый_индекс -> имя_класса
    old_idx_to_name = {}
    for i, class_name in enumerate(as_is_classes):
        old_idx_to_name[i] = class_name
    
    # Создаем словарь новое_имя -> новый_индекс
    new_name_to_idx = {}
    for i, class_name in enumerate(order_new_classes):
        new_name_to_idx[class_name] = i
    
    # Создаем финальный маппинг старый_индекс -> новый_индекс
    old_to_new_mapping = {}
    for old_idx, old_name in old_idx_to_name.items():
        if old_name in remap:
            new_name = remap[old_name]
            if new_name in new_name_to_idx:
                old_to_new_mapping[old_idx] = new_name_to_idx[new_name]
    
    return old_to_new_mapping


def process_annotation_file(src_file, dst_file, class_mapping):
    """
    Обрабатывает один файл аннотации
    
    Args:
        src_file: путь к исходному файлу
        dst_file: путь к файлу назначения
        class_mapping: словарь маппинга классов
    """
    processed_lines = []
    
    with open(src_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        old_class_idx = int(parts[0])
        
        # Если класс есть в маппинге, заменяем
        if old_class_idx in class_mapping:
            new_class_idx = class_mapping[old_class_idx]
            # Заменяем индекс класса на новый
            parts[0] = str(new_class_idx)
            processed_lines.append(' '.join(parts))
        # Если класса нет в маппинге, пропускаем эту строку (удаляем)
    
    # Сохраняем обработанный файл
    with open(dst_file, 'w') as f:
        for line in processed_lines:
            f.write(line + '\n')


def save_classes_file(dst_classes_path, order_new_classes):
    """
    Сохраняет файл с новыми классами
    
    Args:
        dst_classes_path: путь к файлу classes.txt
        order_new_classes: список новых классов в нужном порядке
    """
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(dst_classes_path), exist_ok=True)
    
    with open(dst_classes_path, 'w', encoding='utf-8') as f:
        for class_name in order_new_classes:
            f.write(class_name + '\n')


def main():
    """Основная функция скрипта"""
    config_path = 'config.yaml'
    
    if not os.path.exists(config_path):
        print(f"Файл конфигурации {config_path} не найден!")
        return
    
    # Загружаем конфигурацию
    config = load_config(config_path)
    
    src_annot_dir = config['src_annot_dir']
    dst_annot_dir = config['dst_annot_dir']
    dst_classes = config['dst_classes']
    as_is_classes = config['as_is_classes']
    remap = config['remap']
    order_new_classes = config['order_new_classes']
    
    # Проверяем существование исходной директории
    if not os.path.exists(src_annot_dir):
        print(f"Исходная директория {src_annot_dir} не найдена!")
        return
    
    # Создаем маппинг классов
    class_mapping = create_class_mapping(as_is_classes, remap, order_new_classes)
    
    print(f"Маппинг классов: {class_mapping}")
    print(f"Новые классы: {order_new_classes}")
    
    # Создаем выходную директорию если её нет
    os.makedirs(dst_annot_dir, exist_ok=True)
    
    # Обрабатываем все .txt файлы
    src_path = Path(src_annot_dir)
    dst_path = Path(dst_annot_dir)
    
    processed_files = 0
    for txt_file in src_path.glob('*.txt'):
        dst_file = dst_path / txt_file.name
        print(f"Обработка {txt_file} -> {dst_file}")
        process_annotation_file(txt_file, dst_file, class_mapping)
        processed_files += 1
    
    print(f"Обработано файлов: {processed_files}")
    
    # Сохраняем файл с новыми классами
    save_classes_file(dst_classes, order_new_classes)
    print(f"Файл с классами сохранен: {dst_classes}")
    
    print("Ремаппинг завершен успешно!")


if __name__ == "__main__":
    main()