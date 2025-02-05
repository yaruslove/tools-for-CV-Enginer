import os
import yaml
from pathlib import Path
from ultralytics import YOLO
import shutil

def setup_directories(dst_base, folder_name):
   """Создание структуры директорий для результатов"""
   folder_path = Path(dst_base) / folder_name
   imgs_path = folder_path / 'imgs'
   imgs_drawed_path = folder_path / 'imgs_drawed' 
   labels_path = folder_path / 'labels'
   
   for path in [imgs_path, imgs_drawed_path, labels_path]:
       path.mkdir(parents=True, exist_ok=True)
       
   return folder_path, imgs_path, imgs_drawed_path, labels_path

def process_folder(model, src_folder, dst_base, classes=None, model_params=None):
   """Обработка одной папки с изображениями"""
   folder_name = src_folder.name
   print(f"Processing folder: {folder_name}")
   
   folder_path, imgs_path, imgs_drawed_path, labels_path = setup_directories(dst_base, folder_name)
   
   # Копируем оригинальные изображения
   for img_file in src_folder.glob('*.[jp][pn][g]'):
       shutil.copy2(img_file, imgs_path)
   
   # Базовые параметры предсказания
   predict_params = {
       'source': str(src_folder),
       'save': True,
       'save_txt': True,
       'project': str(folder_path),
       'exist_ok': True,
       'name': 'predict',
       'classes': classes,
       'show_conf': model_params.get('show_conf', False) if model_params else False
   }
   
   # Добавляем параметры модели если они указаны
   if model_params:
       predict_params.update(model_params)
   
   # Запускаем предсказание
   results = model.predict(**predict_params)
   
   # Перемещаем результаты
   pred_dir = folder_path / 'predict'
   if pred_dir.exists():
       for img_file in pred_dir.glob('*.[jp][pn][g]'):
           shutil.move(str(img_file), imgs_drawed_path)
       
       pred_labels = pred_dir / 'labels'
       if pred_labels.exists():
           for label_file in pred_labels.glob('*.txt'):
               shutil.move(str(label_file), labels_path)
       
       shutil.rmtree(pred_dir)

def main(config_path):
   with open(config_path, 'r') as f:
       config = yaml.safe_load(f)
   
   model = YOLO(config['weights_yolo'])
   
   dst_base = Path(config['dst'])
   dst_base.mkdir(parents=True, exist_ok=True)
   
   classes = config.get('classes', None)
   model_params = config.get('model_params', None)
   
   src_base = Path(config['src'])
   for folder in src_base.iterdir():
       if folder.is_dir():
           process_folder(model, folder, dst_base, classes, model_params)

if __name__ == "__main__":
   main('config.yaml')