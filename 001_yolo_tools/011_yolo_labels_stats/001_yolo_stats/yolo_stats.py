import os
import yaml
from collections import Counter
from pathlib import Path

def analyze_yolo_labels(labels_path, classes):
   # Счетчик для классов
   class_counts = Counter()
   
   # Проходим по всем txt файлам в директории
   for txt_file in Path(labels_path).glob('*.txt'):
       with open(txt_file, 'r') as f:
           for line in f:
               # YOLO формат: class_id x y w h
               class_id = int(line.split()[0])
               class_counts[class_id] += 1
   
   # Подсчет общего количества
   total = sum(class_counts.values())
   
   # Вывод статистики
   print("\nCounts:")
   for class_id, count in sorted(class_counts.items()):
       class_name = classes[class_id]
       print(f"cl {class_id} {class_name} : {count}")
   print(f"Total: {total}\n")
   
   print("Percentages:")
   for class_id, count in sorted(class_counts.items()):
       class_name = classes[class_id]
       percentage = (count / total) * 100
       print(f"cl {class_id} {class_name} : {percentage:.1f}%")

if __name__ == "__main__":
   # Загрузка конфига
   with open("config.yaml", 'r') as f:
       config = yaml.safe_load(f)
   
   # Получение пути и классов из конфига
   labels_path = config['path_labels']
   classes = config['classes']
   
   # Анализ данных
   analyze_yolo_labels(labels_path, classes)