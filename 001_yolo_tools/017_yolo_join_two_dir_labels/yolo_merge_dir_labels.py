import os
from pathlib import Path
import yaml

class YoloLabelsMerger:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        
        # Создание атрибутов путей
        self.dir_labels1 = Path(self.config['dir_labels1'])
        self.dir_labels2 = Path(self.config['dir_labels2'])
        self.output_dir = Path(self.config['dst_save_labels'])
        
        self.output_dir.mkdir(exist_ok=True)
        self.class_remapping = self._build_class_remapping()
    
    def _load_config(self, config_path):
        """Загрузка конфигурации из YAML файла"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _build_class_remapping(self):
        """Создание маппинга для переназначения классов"""
        remapping = {}
        
        # Маппинг для первой папки
        for old_class, class_name in self.config['as_is_labels1_classes'].items():
            new_class = self._find_new_class_id(class_name)
            remapping[('labels1', old_class)] = new_class
        
        # Маппинг для второй папки
        for old_class, class_name in self.config['as_is_labels2_classes'].items():
            new_class = self._find_new_class_id(class_name)
            remapping[('labels2', old_class)] = new_class
            
        return remapping
    
    def _find_new_class_id(self, class_name):
        """Поиск нового ID класса по имени"""
        for class_id, name in self.config['to_be_joined_classes'].items():
            if name == class_name:
                return class_id
        raise ValueError(f"Класс {class_name} не найден в to_be_joined_classes")
    
    def _process_txt_file(self, file_path, source_folder):
        """Обработка одного txt файла с переназначением классов"""
        if not file_path.exists():
            return []
        
        processed_lines = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    old_class = int(parts[0])
                    new_class = self.class_remapping[(source_folder, old_class)]
                    parts[0] = str(new_class)
                    processed_lines.append(' '.join(parts) + '\n')
        return processed_lines
    
    def _get_all_txt_files(self):
        """Получение списка всех txt файлов из обеих папок"""
        files1 = set(f.name for f in self.dir_labels1.glob('*.txt'))
        files2 = set(f.name for f in self.dir_labels2.glob('*.txt'))
        
        return files1.union(files2)
    
    def _merge_file_content(self, filename):
        """Мерж содержимого файла из обеих папок"""
        merged_lines = []
        
        # Обработка из первой папки
        file1_path = self.dir_labels1 / filename
        merged_lines.extend(self._process_txt_file(file1_path, 'labels1'))
        
        # Обработка из второй папки
        file2_path = self.dir_labels2 / filename
        merged_lines.extend(self._process_txt_file(file2_path, 'labels2'))
        
        return merged_lines
    
    def _write_merged_file(self, filename, lines):
        """Запись объединенного файла"""
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            f.writelines(lines)
    
    def merge_all_labels(self):
        """Основной метод для мержа всех разметок"""
        all_files = self._get_all_txt_files()
        
        for filename in all_files:
            merged_content = self._merge_file_content(filename)
            if merged_content:  # Только если есть содержимое
                self._write_merged_file(filename, merged_content)
        
        print(f"Объединение завершено. Результат сохранен в папке: {self.output_dir}")

# Использование:
merger = YoloLabelsMerger('config.yaml')
merger.merge_all_labels()