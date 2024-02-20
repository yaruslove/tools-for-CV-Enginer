import os
from utils import path_to_dict, compare_sets_common, renamer, read_yaml


def rename_collection(path_in, path_out, prefix):
    """
    input to function: path: str
    path contain dirs: images and labels
    path/
        │
        ├── classes.txt
        │
        ├── images
        │   ├── 28032449.jpg
        │   ├── .....
        │   └── 29163987.jpg
        │
        └── labels
            ├── 28032449.txt
            ├── .....
            └── 29163987.jpg

    """
    path_labels = os.path.join(path_in, "labels")
    path_images = os.path.join(path_in, "images")
    
    labels_dict = path_to_dict(path_labels)
    images_dict = path_to_dict(path_images)
    
    common_items=compare_sets_common(labels_dict, images_dict)
    
    # rename
    renamer(path_in,
            path_out,
            labels_dict,
            images_dict,
            common_items,
            prefix)
    
data = read_yaml(config='config.yaml')
print(data)
path_in = data["path_in"]
path_out = data["path_out"]
prefix = data["prefix"]


rename_collection(path_in, path_out, prefix)