import yaml
import cv2
import numpy as np
from pathlib import Path

def read_config(config_path):
   """Чтение конфига и извлечение упорядоченных пар src-text"""
   with open(config_path, 'r') as f:
       config = yaml.safe_load(f)
   
   # Извлекаем пары src-text
   pairs = []
   i = 1
   while True:
       src_key = f"{i:03d}_src"
       text_key = f"{i:03d}_printed_text"
       
       if src_key not in config or text_key not in config:
           break
           
       pairs.append((config[src_key], config[text_key]))
       i += 1
   
   if len(pairs) < 2:
       raise ValueError("Need at least 2 source directories")
       
   return pairs, config['dst']

def join_images_with_text(image_name, src_text_pairs, dst_path):
   """Объединение изображений с текстом"""
   images = []
   texts = []
   max_height = 0
   total_width = 0
   padding_height = 40  # Высота области для текста
   
   # Читаем все изображения
   for src_path, text in src_text_pairs:
       img_path = Path(src_path) / image_name
       if not img_path.exists():
           print(f"Warning: {img_path} not found")
           return
           
       img = cv2.imread(str(img_path))
       if img is None:
           print(f"Warning: Could not read {img_path}")
           return
           
       images.append(img)
       texts.append(text)
       
       h, w = img.shape[:2]
       max_height = max(max_height, h)
       total_width += w

   # Создаем итоговое изображение с padding для текста
   result = np.ones((max_height + padding_height, total_width, 3), dtype=np.uint8) * 255
   
   # Объединяем изображения и добавляем текст
   x_offset = 0
   font = cv2.FONT_HERSHEY_SIMPLEX
   font_scale = 0.7
   font_thickness = 2
   
   for idx, (img, text) in enumerate(zip(images, texts)):
       h, w = img.shape[:2]
       
       # Размещаем изображение
       result[padding_height:padding_height+h, x_offset:x_offset+w] = img
       
       # Добавляем текст
       text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
       text_x = x_offset + (w - text_size[0]) // 2
       text_y = padding_height // 2 + text_size[1] // 2
       
       cv2.putText(result, text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)
       
       x_offset += w
   
   # Сохраняем результат
   dst_path = Path(dst_path)
   dst_path.mkdir(parents=True, exist_ok=True)
   cv2.imwrite(str(dst_path / image_name), result)

def process_all_images(config_path):
   """Обработка всех изображений"""
   # Читаем конфиг
   src_text_pairs, dst_path = read_config(config_path)
   
   # Получаем список изображений из первой директории
   first_src = Path(src_text_pairs[0][0])
   image_files = list(first_src.glob('*.[jp][pn][g]'))
   
   # Обрабатываем каждое изображение
   for img_path in image_files:
       print(f"Processing {img_path.name}")
       join_images_with_text(img_path.name, src_text_pairs, dst_path)

if __name__ == "__main__":
   process_all_images('config.yaml')