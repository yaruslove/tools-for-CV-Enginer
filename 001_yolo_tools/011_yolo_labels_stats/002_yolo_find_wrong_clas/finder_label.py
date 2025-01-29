import os
import yaml
from pathlib import Path

def find_labels_with_class(labels_path, target_class):
   # Список для хранения имен файлов
   files_with_class = []
   
   # Проходим по всем txt файлам
   for txt_file in Path(labels_path).glob('*.txt'):
       with open(txt_file, 'r') as f:
           # Читаем все строки файла
           content = f.readlines()
           
           # Проверяем каждую строку на наличие целевого класса
           for line in content:
               class_id = int(line.split()[0])
               if class_id == target_class:
                   files_with_class.append(txt_file.name)
                   break  # Если нашли класс, переходим к следующему файлу
   
   # Вывод результатов
   print(f"\nFiles containing class_id {target_class}:")
   for filename in sorted(files_with_class):
       print(filename)
   print(f"\nTotal files: {len(files_with_class)}")

if __name__ == "__main__":
   # Загрузка конфига
   with open("config.yaml", 'r') as f:
       config = yaml.safe_load(f)
   
   # Получение параметров из конфига
   labels_path = config['path_labels']
   target_class = config['class_id']
   
   # Анализ данных
   find_labels_with_class(labels_path, target_class)