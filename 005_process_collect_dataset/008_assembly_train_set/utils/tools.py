import os
import yaml
import pandas as pd
from natsort import natsorted, ns



def remove_ds_store(directory):
    """
    Safely removes all .DS_Store files in the given directory and subdirectories
    Args:
        directory (str): Root directory path to start searching from. Defaults to current directory.
    Returns:
        list: List of removed .DS_Store file paths
    """
    removed_files = []
    
    try:
        # Walk through directory tree
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == ".DS_Store":
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        removed_files.append(file_path)
                        # print(f"Removed: {file_path}")
                    except OSError as e:
                        pass
                        # print(f"Error removing {file_path}: {e}")
                        
    except Exception as e:
        print(f"Error walking through directory {directory}: {e}")
        
    return removed_files



def read_data(path_src, path_final_data):  
    path_txt = os.path.join(path_src, path_final_data)
    if os.path.exists(path_txt):
        with open(path_txt, "r") as file:
            path_line = file.readlines()[0] ##.split("/")
        path_final = os.path.join(path_src, path_line)
        return path_final
    else:
        return None
    

def get_yaml_config(pth):
    with open(pth, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def get_only_directories(path):
    # Get all directories from the specified path
    directories = [d for d in os.listdir(path) 
                  if os.path.isdir(os.path.join(path, d))]
    return directories


def prep_columns(classes):
    classes = list(map(str, classes))
    classes = natsorted(classes, alg=ns.IGNORECASE) 
    columns = ['name'] + classes
    return columns



def create_df_asis(columns, list_sources, path_data, path_final_data, classes):
    df_asis = pd.DataFrame(columns=columns)  # создаем пустой DataFrame
    # df_asis = df_asis.reindex(columns=columns)

    for source in list_sources: # DIRS: 001_AM, 002_ECO, 003_iphone
        path_src = os.path.join(path_data, source)
        path_classes = read_data(path_src, path_final_data)
        if path_classes is None:
            print(f"Path is't exist {path_classes}")
            continue
        # print(f"path_classes {path_classes}")

        # list_classes = os.listdir(path_classes)
        list_classes = get_only_directories(path_classes)

        dict_amount = {}
        dict_amount['name'] = source
        
        # Проверка на отсутвсие лишних классов
        assert_contains_all(classes, list_classes)

        for cl_name in list_classes: # classes 1, 2, 3, 4, 5, 6, 7
            path_images = os.path.join(path_classes, cl_name)
            # print(f"path_images {path_images}")
            # classes_dirs = get_only_directories(path_images)
            list_imgs = os.listdir(path_images)
            # print(f"list_imgs {list_imgs}")
            len_images_cls = len(os.listdir(path_images))
            dict_amount[cl_name] = len_images_cls

        # df_asis = df_asis.append(dict_amount, ignore_index=True)
        df_asis = pd.concat([df_asis, pd.DataFrame([dict_amount])], ignore_index=True)
    return df_asis

def safly_create_dir(path_out):
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    else:
        assert not os.path.exists(path_out), f"Path {path_out} alredy exist !!! Change name dir"


def assert_contains_all(container, required_elements):
    # Приведем все к строкам
    container = list(map(str, container))
    required_elements = list(map(str, required_elements))

    assert set(required_elements).issubset(set(container)), \
        f"Несуществующие elements: {set(required_elements) - set(container)}"



def count_totalsum(df):
    """
    Добавляет строку с суммами для всех числовых столбцов в DataFrame
    
    Args:
        df (pd.DataFrame): Исходный DataFrame
    
    Returns:
        pd.DataFrame: DataFrame с добавленной строкой сумм
    """
    # Создаем копию DataFrame
    df = df.copy()
    
    # Определяем числовые столбцы (все кроме 'name')
    numeric_columns = [col for col in df.columns if col != 'name']
    
    # Создаем словарь для новой строки
    total_dict = {'name': 'total_sum'}
    
    # Вычисляем суммы для каждого числового столбца
    for col in numeric_columns:
        # Преобразуем столбец в числовой формат, игнорируя ошибки
        total_dict[col] = pd.to_numeric(df[col], errors='coerce').sum()
    
    # Добавляем строку с суммами
    df.loc[len(df)] = total_dict
    
    return df

