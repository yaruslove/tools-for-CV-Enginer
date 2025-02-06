from pathlib import Path
import yaml
from ultralytics import YOLO
import cv2
import os
import torch
import numpy as np

def load_config(config_path: str) -> dict:
   """Загрузка конфигурации из YAML файла"""
   with open(config_path, 'r') as f:
       config = yaml.safe_load(f)
   return config

def draw_boxes(image, boxes, classes_dict, colors, vis_params):
   """Отрисовка боксов на изображении с названиями классов"""
   img = image.copy()
   
   box_thickness = vis_params.get('box_thickness', 2)
   font_scale = vis_params.get('font_scale', 0.5)
   font_thickness = vis_params.get('font_thickness', 1)
   
   for box in boxes:
       cls = int(box.cls.item())
       # Проверяем наличие класса в словаре
       if cls in classes_dict:
           x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
           conf = float(box.conf[0])
           color = tuple(reversed(colors[cls]))
           
           cv2.rectangle(img, (x1, y1), (x2, y2), color, box_thickness)
           # Используем название класса из словаря
           label = f"{classes_dict[cls]}: {conf:.2f}"
           cv2.putText(img, label, (x1, y1-10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 
                      font_scale, 
                      color, 
                      font_thickness)
   return img

def process_images(config: dict):
   device = f"cuda:{config['device']}" if torch.cuda.is_available() and 'device' in config else "cpu"
   
   model = YOLO(config['weights_yolo'])
   model.to(device)
   
   os.makedirs(config['dst'], exist_ok=True)
   if config.get('visulise', {}).get('do', False):
       os.makedirs(config['visulise']['visulise_path'], exist_ok=True)
   
   src_dir = Path(config['src'])
   image_files = list(src_dir.glob('*.jpg')) + list(src_dir.glob('*.png'))
   
   # Получаем словарь классов
   classes_dict = config.get('classes', {})
   # Преобразуем строковые ключи в целые числа, если они есть
   classes_dict = {int(k): v for k, v in classes_dict.items()}
   
   allowed_classes = set(classes_dict.keys())  # Используем ключи словаря как разрешенные классы
   colors = config.get('colors', [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]])
   model_params = config.get('model_params', {})
   visualise_config = config.get('visulise', {})
   
   vis_params = {
       'box_thickness': visualise_config.get('box_thickness', 2),
       'font_scale': visualise_config.get('font_scale', 0.5),
       'font_thickness': visualise_config.get('font_thickness', 1)
   }
   
   for img_path in image_files:
       if visualise_config.get('do', False):
           orig_img = cv2.imread(str(img_path))
       
       results = model.predict(
           source=str(img_path),
           conf=model_params.get('conf', 0.25),
           iou=model_params.get('iou', 0.45),
           agnostic_nms=model_params.get('agnostic_nms', False),
           device=device
       )
       
       for r in results:
           if r.boxes is not None and len(r.boxes) > 0:
               labels_path = Path(config['dst']) / f"{img_path.stem}.txt"
               with open(labels_path, 'w') as f:
                   for box in r.boxes:
                       cls = int(box.cls.item())
                       if cls in allowed_classes:  # Проверяем наличие класса в словаре
                           x, y, w, h = box.xywhn[0].tolist()
                           f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
               
               if visualise_config.get('do', False):
                   vis_img = draw_boxes(orig_img, r.boxes, classes_dict, colors, vis_params)
                   vis_path = Path(visualise_config['visulise_path']) / f"{img_path.stem}_vis{img_path.suffix}"
                   cv2.imwrite(str(vis_path), vis_img)

def main():
   config = load_config('config.yaml')
   print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
   print(f"Processing classes: {config.get('classes', {})}")
   process_images(config)

if __name__ == "__main__":
   main()