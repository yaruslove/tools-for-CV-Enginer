import os
from utils import path_to_dict, compare_sets_common, mover_ImgsLabls, read_yaml


def split_dataset(path_in, path_out, transfer_percentage):
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
    mover_ImgsLabls(path_in,
            path_out,
            labels_dict,
            images_dict,
            common_items,
            transfer_percentage)
    
data = read_yaml(config='config.yaml')
print(data)
path_in = data["path_in"]
path_out = data["path_out"]
transfer_percentage = data["transfer_percentage"]


split_dataset(path_in, path_out, transfer_percentage)