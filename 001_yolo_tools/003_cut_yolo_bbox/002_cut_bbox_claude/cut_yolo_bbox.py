import glob
import os
import cv2
import yaml
from tqdm import tqdm

def load_config(config_path):
    """Загрузка конфигурации из YAML файла"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def is_valid_image(img_path):
    """Проверка валидности изображения"""
    img = cv2.imread(img_path)
    return img is not None and img.size > 0

def is_valid_bbox(x1, y1, x2, y2, w, h):
    """Проверка валидности координат bbox"""
    xstrt = max(0, int((x1 - x2/2) * w))
    xend = min(w, int((x1 + x2/2) * w))
    ystrt = max(0, int((y1 - y2/2) * h))
    yend = min(h, int((y1 + y2/2) * h))
    return xstrt < xend and ystrt < yend, (xstrt, xend, ystrt, yend)

if __name__ == '__main__':
    # Загрузка конфигурации
    config = load_config('config.yaml')
    
    labels_pth = config['labels_pth']
    imgs_pth = config['imgs_pth']
    out_pth = config['out_pth']
    classes = {int(k): v for k, v in config['classes'].items()}

    labels_pth = glob.glob(f"{labels_pth}/*.txt")
    
    # Статистика
    no_image = []
    invalid_boxes = []
    processed_files = 0
    processed_boxes = 0
    invalid_box_count = 0

    # Создание директорий для классов
    for pth_cl in classes.values():
        pth_cl = os.path.join(out_pth, pth_cl)
        if not os.path.exists(pth_cl):
            os.makedirs(pth_cl)

    pbar = tqdm(labels_pth)
    for cur_lab in pbar:
        if cur_lab.endswith("classes.txt"):
            continue
            
        name_file = os.path.basename(cur_lab)
        pbar.set_postfix({'file': name_file})
        name_file = name_file[:name_file.rfind(".")]
        
        # Поиск соответствующего изображения
        img_path = None
        for img_name in os.listdir(imgs_pth):
            if img_name.startswith(name_file+".") and not img_name.endswith(".txt"):
                img_path = os.path.join(imgs_pth, img_name)
                break
             
        if img_path is None or not is_valid_image(img_path):      
            no_image.append(name_file)
            continue
        
        img = cv2.imread(img_path)
        h, w, _ = img.shape
        
        # Чтение файла меток
        with open(cur_lab, 'r') as f:
            lines = f.read().strip().split("\n")
        
        if len(lines) < 1:
            continue

        processed_files += 1
        
        for idx, line in enumerate(lines):
            parts = line.strip().split()
            if len(parts) != 5 or not all(p.replace('.', '').isdigit() for p in parts):
                invalid_boxes.append(f"{name_file}: неверный формат строки - {line}")
                invalid_box_count += 1
                continue
                
            cl, x1, y1, x2, y2 = map(float, parts)
            
            if int(cl) not in classes:
                continue
                
            # Проверка и получение координат bbox
            is_valid, coords = is_valid_bbox(x1, y1, x2, y2, w, h)
            if not is_valid:
                invalid_boxes.append(f"{name_file}: некорректные координаты - {line}")
                invalid_box_count += 1
                continue
                
            xstrt, xend, ystrt, yend = coords
            tmp_img = img[ystrt:yend, xstrt:xend]
            
            if tmp_img.size == 0:
                invalid_boxes.append(f"{name_file}: пустая область - {line}")
                invalid_box_count += 1
                continue

            # Сохранение вырезанного изображения
            tmp_outpath = os.path.join(out_pth, classes[int(cl)], f"{name_file}_{idx}.png")
            if cv2.imwrite(tmp_outpath, tmp_img):
                processed_boxes += 1
            else:
                invalid_boxes.append(f"{name_file}: ошибка сохранения - {line}")
                invalid_box_count += 1

    # Вывод статистики
    print("\nСтатистика обработки:")
    print(f"Обработано файлов: {processed_files}")
    print(f"Успешно обработано bbox: {processed_boxes}")
    print(f"Количество файлов без изображений: {len(no_image)}")
    print(f"Количество некорректных bbox: {invalid_box_count}")
    
    if no_image:
        print("\nСписок файлов без изображений:")
        print('\n'.join(no_image))
    
    if invalid_boxes:
        print("\nСписок некорректных bbox:")
        print('\n'.join(invalid_boxes))
            
    print("\nПрограмма завершена!")