from pathlib import Path
import yaml
from ultralytics import YOLO
import cv2
import os
import torch

def load_config(config_path: str) -> dict:
   """Загрузка конфигурации из YAML файла"""
   with open(config_path, 'r') as f:
       config = yaml.safe_load(f)
   return config

def process_images(config: dict):
   """Обработка изображений с помощью YOLO"""
   # Установка устройства
   device = f"cuda:{config['device']}" if torch.cuda.is_available() and 'device' in config else "cpu"
   
   # Загрузка модели
   model = YOLO(config['weights_yolo'])
   model.to(device)  # перемещение модели на GPU
   
   # Создание выходной директории если её нет
   os.makedirs(config['dst'], exist_ok=True)
   
   # Получение списка изображений
   src_dir = Path(config['src'])
   image_files = list(src_dir.glob('*.jpg')) + list(src_dir.glob('*.png'))
   
   # Параметры модели
   model_params = config.get('model_params', {})
   
   # Обработка каждого изображения
   for img_path in image_files:
       # Предсказание
       results = model.predict(
           source=str(img_path),
           conf=model_params.get('conf', 0.25),
           iou=model_params.get('iou', 0.45),
           agnostic_nms=model_params.get('agnostic_nms', False),
           device=device
       )
       
       # Сохранение результатов в формате YOLO
       for r in results:
           labels_path = Path(config['dst']) / f"{img_path.stem}.txt"
           
           if r.boxes is not None and len(r.boxes) > 0:
               with open(labels_path, 'w') as f:
                   for box in r.boxes:
                       # Получение класса и координат
                       cls = int(box.cls.item())
                       x, y, w, h = box.xywhn[0].tolist()  # нормализованные координаты
                       
                       # Запись в формате YOLO: class x_center y_center width height
                       f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

def main():
   config = load_config('config.yaml')
   print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
   process_images(config)

if __name__ == "__main__":
   main()