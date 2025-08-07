import os
import yaml
from pathlib import Path
from typing import List, Tuple, Optional


def load_config(config_path: str = "config.yaml") -> dict:
    """Загрузка конфигурации из YAML файла."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def parse_yolo_line(line: str) -> Tuple[int, float, float, float, float]:
    """
    Парсинг строки YOLO формата.
    Возвращает: (class_id, x_center, y_center, width, height)
    """
    parts = line.strip().split()
    class_id = int(parts[0])
    x_center = float(parts[1])
    y_center = float(parts[2])
    width = float(parts[3])
    height = float(parts[4])
    return class_id, x_center, y_center, width, height


def format_yolo_line(class_id: int, x_center: float, y_center: float, 
                     width: float, height: float) -> str:
    """Форматирование bbox в строку YOLO формата."""
    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def bbox_to_corners(x_center: float, y_center: float, 
                   width: float, height: float) -> Tuple[float, float, float, float]:
    """
    Конвертация YOLO bbox (центр + размеры) в координаты углов.
    Возвращает: (x_min, y_min, x_max, y_max)
    """
    x_min = x_center - width / 2
    y_min = y_center - height / 2
    x_max = x_center + width / 2
    y_max = y_center + height / 2
    return x_min, y_min, x_max, y_max


def calculate_iou(bbox1: Tuple[float, float, float, float], 
                 bbox2: Tuple[float, float, float, float]) -> float:
    """
    Вычисление Intersection over Union (IoU) между двумя bbox.
    bbox формат: (x_center, y_center, width, height)
    """
    # Конвертируем в координаты углов
    x1_min, y1_min, x1_max, y1_max = bbox_to_corners(*bbox1)
    x2_min, y2_min, x2_max, y2_max = bbox_to_corners(*bbox2)
    
    # Вычисляем координаты пересечения
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    # Если нет пересечения
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0
    
    # Площадь пересечения
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    
    # Площади bbox
    bbox1_area = bbox1[2] * bbox1[3]  # width * height
    bbox2_area = bbox2[2] * bbox2[3]
    
    # Площадь объединения
    union_area = bbox1_area + bbox2_area - inter_area
    
    # IoU
    if union_area == 0:
        return 0.0
    
    iou = inter_area / union_area
    return iou


def find_best_head_for_helmet(helmet_bbox: Tuple[float, float, float, float],
                              head_bboxes: List[Tuple[int, Tuple[float, float, float, float]]]) -> Optional[int]:
    """
    Найти индекс Head bbox с максимальным IoU для данного Helmet bbox.
    
    Args:
        helmet_bbox: bbox координаты helmet (x_center, y_center, width, height)
        head_bboxes: список кортежей (индекс, bbox координаты) для головы
    
    Returns:
        Индекс head bbox с максимальным IoU или None если нет пересечений
    """
    if not head_bboxes:
        return None
    
    best_idx = None
    max_iou = 0.0
    
    for idx, head_bbox in head_bboxes:
        iou = calculate_iou(helmet_bbox, head_bbox)
        if iou > max_iou:
            max_iou = iou
            best_idx = idx
    
    # Возвращаем только если есть реальное пересечение
    if max_iou > 0:
        return best_idx
    return None


def process_labels_file(input_path: str, output_path: str) -> None:
    """
    Обработка одного файла разметки YOLO.
    
    Логика:
    1. Для каждого Helmet (class_id=2) ищем парный Head (class_id=1) с max IoU
    2. Если пара найдена:
       - Удаляем Helmet bbox
       - Меняем класс Head на Helmet (1 -> 2)
    3. Если пара не найдена - оставляем Helmet без изменений
    """
    # Читаем все строки из файла
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    # Парсим все bbox
    bboxes = []
    for line in lines:
        if line.strip():
            bbox_data = parse_yolo_line(line)
            bboxes.append(bbox_data)
    
    # Разделяем bbox по классам
    # class_id: 0 = Person, 1 = Head, 2 = Helmet
    helmet_indices = []
    head_indices = []
    
    for i, bbox in enumerate(bboxes):
        class_id = bbox[0]
        if class_id == 2:  # Helmet
            helmet_indices.append(i)
        elif class_id == 1:  # Head
            head_indices.append(i)
    
    # Подготавливаем список head bbox с их индексами
    head_bboxes_with_idx = [(i, bboxes[i][1:]) for i in head_indices]
    
    # Находим пары Helmet-Head
    pairs_to_process = []  # (helmet_idx, head_idx)
    
    for helmet_idx in helmet_indices:
        helmet_bbox = bboxes[helmet_idx][1:]  # (x_center, y_center, width, height)
        best_head_idx = find_best_head_for_helmet(helmet_bbox, head_bboxes_with_idx)
        
        if best_head_idx is not None:
            pairs_to_process.append((helmet_idx, best_head_idx))
    
    # Применяем изменения
    indices_to_remove = set()
    class_changes = {}  # {index: new_class_id}
    
    for helmet_idx, head_idx in pairs_to_process:
        # Удаляем Helmet
        indices_to_remove.add(helmet_idx)
        # Меняем класс Head на Helmet (1 -> 2)
        class_changes[head_idx] = 2
    
    # Формируем результирующий список bbox
    result_bboxes = []
    for i, bbox in enumerate(bboxes):
        if i in indices_to_remove:
            continue  # Пропускаем удаленные bbox
        
        # Применяем изменение класса если необходимо
        if i in class_changes:
            new_bbox = (class_changes[i], *bbox[1:])
            result_bboxes.append(new_bbox)
        else:
            result_bboxes.append(bbox)
    
    # Записываем результат
    with open(output_path, 'w') as f:
        for bbox in result_bboxes:
            line = format_yolo_line(*bbox)
            f.write(line + '\n')


def main():
    """Основная функция скрипта."""
    # Загружаем конфигурацию
    config = load_config("config.yaml")
    src_dir = Path(config['src_annot_dir'])
    dst_dir = Path(config['dst_annot_dir'])
    
    # Создаем выходную директорию если не существует
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    # Получаем список всех .txt файлов
    txt_files = list(src_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"Не найдено .txt файлов в директории {src_dir}")
        return
    
    print(f"Найдено {len(txt_files)} файлов для обработки")
    
    # Обрабатываем каждый файл
    for txt_file in txt_files:
        input_path = str(txt_file)
        output_path = str(dst_dir / txt_file.name)
        
        try:
            process_labels_file(input_path, output_path)
            print(f"Обработан: {txt_file.name}")
        except Exception as e:
            print(f"Ошибка при обработке {txt_file.name}: {e}")
    
    print(f"\nОбработка завершена. Результаты сохранены в {dst_dir}")


if __name__ == "__main__":
    main()