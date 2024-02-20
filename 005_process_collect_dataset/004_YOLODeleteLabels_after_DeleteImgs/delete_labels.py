import os
from utils import path_to_dict, compare_sets_dif, delete_dif_labels, read_yaml


def delete_labels(path_in):
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
    
    dif=compare_sets_dif(labels_dict, images_dict)
    
    # rename
    delete_dif_labels(dif, path_in, labels_dict)
    
data = read_yaml(config='config.yaml')
print(data)
path_in = data["path_in"]


delete_labels(path_in)