import os
import shutil
import secrets
import string
import cv2 as cv
import yaml

from tqdm import tqdm


def read_yaml(config='config.yaml'):
    with open(config) as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data


def split_name(name):
    end_point = name.rfind(".")
    base_name, ext = name[:end_point], name[end_point:]
    return base_name, ext


def path_to_dict(path):
    base_names=dict()
    for i in os.listdir(path):
        base_name, ext = split_name(i)
        base_names[base_name] = ext
    return base_names

def compare_sets_dif(label_dict, image_dict):
    labels_names = set(label_dict.keys())
    images_names = set(image_dict.keys())

    dif = list(labels_names - images_names)

    print(f"Amount")
    print(f"labels: {len(labels_names)}")
    print(f"images: {len(images_names)}")
    print(f"dif item: {len(dif)}")
    print(f"difference labeles with imgs is: {dif}")
    
    return dif

def create_path_out(path_out):
    dst_labels = os.path.join(path_out,"labels")
    dst_imgs = os.path.join(path_out,"images")
    if not os.path.isdir(dst_labels):
        os.mkdir(dst_labels) 
    if not os.path.isdir(dst_imgs):
        os.mkdir(dst_imgs)
    return dst_labels, dst_imgs

    
def delete_dif_labels(dif, path_in, labels_dict):
    del_labels="deleted_labels"
    path_del_lbl =os.path.join(path_in, del_labels)
    if not os.path.isdir(path_del_lbl):
        os.mkdir(path_del_lbl)

    for i in dif:
        if labels_dict[i]==".txt":
            i=i+".txt"
            src_lbl = os.path.join(path_in, "labels", i)
            dst_lbl = os.path.join(path_del_lbl, i)
            # shutil.copy(src_lbl, dst_lbl)
            shutil.move(src_lbl, dst_lbl)

    print(f"Task has done! 🎉")
        
        