import os
import shutil
import yaml
import logging
from pathlib import Path
from tqdm import tqdm

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataReorganizer:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.validate_config()
        
    def load_config(self, config_path):
        """Загрузка конфигурации из YAML файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logging.info(f"Конфигурация загружена из {config_path}")
                return config
        except Exception as e:
            logging.error(f"Ошибка загрузки конфигурации: {str(e)}")
            raise

    def validate_config(self):
        """Проверка конфигурации и путей"""
        required_paths = ['src_imgs', 'src_labels', 'src_classes', 'joined']
        
        # Проверка наличия всех необходимых параметров
        missing = [path for path in required_paths if path not in self.config]
        if missing:
            raise ValueError(f"Отсутствуют обязательные параметры в конфигурации: {missing}")

        # Проверка существования исходных директорий
        if not os.path.exists(self.config['src_imgs']):
            raise FileNotFoundError(f"Директория изображений не найдена: {self.config['src_imgs']}")
        
        if not os.path.exists(self.config['src_labels']):
            raise FileNotFoundError(f"Директория разметки не найдена: {self.config['src_labels']}")
            
        if not os.path.exists(self.config['src_classes']):
            raise FileNotFoundError(f"Файл classes.txt не найден: {self.config['src_classes']}")

    def create_directory_structure(self):
        """Создание структуры директорий"""
        try:
            # Получаем список поддиректорий из src_imgs
            subdirs = [d for d in os.listdir(self.config['src_imgs']) 
                      if os.path.isdir(os.path.join(self.config['src_imgs'], d))]
            
            logging.info(f"Найдено {len(subdirs)} поддиректорий для обработки")
            
            # Создаём базовую выходную директорию
            os.makedirs(self.config['joined'], exist_ok=True)
            
            for subdir in tqdm(subdirs, desc="Создание структуры директорий"):
                # Создаём поддиректории для images и labels
                joined_subdir = os.path.join(self.config['joined'], subdir)
                images_dir = os.path.join(joined_subdir, 'images')
                labels_dir = os.path.join(joined_subdir, 'labels')
                
                os.makedirs(images_dir, exist_ok=True)
                os.makedirs(labels_dir, exist_ok=True)
                
            return subdirs
        
        except Exception as e:
            logging.error(f"Ошибка при создании структуры директорий: {str(e)}")
            raise

    def copy_files(self, subdirs):
        """Копирование файлов в новую структуру"""
        try:
            for subdir in tqdm(subdirs, desc="Копирование файлов"):
                # Пути к исходным директориям
                src_img_dir = os.path.join(self.config['src_imgs'], subdir)
                src_label_dir = os.path.join(self.config['src_labels'], subdir)
                
                # Пути к целевым директориям
                dst_img_dir = os.path.join(self.config['joined'], subdir, 'images')
                dst_label_dir = os.path.join(self.config['joined'], subdir, 'labels')
                
                # Копирование изображений
                for img in os.listdir(src_img_dir):
                    if img.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        shutil.copy2(
                            os.path.join(src_img_dir, img),
                            os.path.join(dst_img_dir, img)
                        )
                
                # Копирование файлов разметки
                for label in os.listdir(src_label_dir):
                    if label.endswith('.txt'):
                        shutil.copy2(
                            os.path.join(src_label_dir, label),
                            os.path.join(dst_label_dir, label)
                        )
                
                # Копирование classes.txt
                shutil.copy2(
                    self.config['src_classes'],
                    os.path.join(self.config['joined'], subdir, 'classes.txt')
                )
                
        except Exception as e:
            logging.error(f"Ошибка при копировании файлов: {str(e)}")
            raise

    def verify_copy(self, subdirs):
        """Проверка корректности копирования"""
        for subdir in subdirs:
            src_img_dir = os.path.join(self.config['src_imgs'], subdir)
            src_label_dir = os.path.join(self.config['src_labels'], subdir)
            dst_img_dir = os.path.join(self.config['joined'], subdir, 'images')
            dst_label_dir = os.path.join(self.config['joined'], subdir, 'labels')
            
            # Проверка количества файлов
            src_imgs = len([f for f in os.listdir(src_img_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            src_labels = len([f for f in os.listdir(src_label_dir) if f.endswith('.txt')])
            dst_imgs = len([f for f in os.listdir(dst_img_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            dst_labels = len([f for f in os.listdir(dst_label_dir) if f.endswith('.txt')])
            
            if src_imgs != dst_imgs or src_labels != dst_labels:
                logging.warning(
                    f"Несоответствие количества файлов в {subdir}:\n"
                    f"Изображения: {src_imgs} -> {dst_imgs}\n"
                    f"Разметка: {src_labels} -> {dst_labels}"
                )
            
            # Проверка наличия classes.txt
            if not os.path.exists(os.path.join(self.config['joined'], subdir, 'classes.txt')):
                logging.warning(f"Отсутствует classes.txt в {subdir}")

    def process(self):
        """Основной метод обработки"""
        try:
            logging.info("Начало обработки данных")
            
            # Создание структуры директорий
            subdirs = self.create_directory_structure()
            
            # Копирование файлов
            self.copy_files(subdirs)
            
            # Проверка результатов
            self.verify_copy(subdirs)
            
            logging.info("Обработка данных завершена успешно")
            
        except Exception as e:
            logging.error(f"Ошибка при обработке данных: {str(e)}")
            raise

def main():
    config_path = 'config.yaml'
    try:
        reorganizer = DataReorganizer(config_path)
        reorganizer.process()
    except Exception as e:
        logging.error(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()