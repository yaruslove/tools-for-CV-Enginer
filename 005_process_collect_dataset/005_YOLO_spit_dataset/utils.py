import os
import shutil
import secrets
import string
import cv2 as cv
import yaml
import random

from tqdm import tqdm


def read_yaml(config='config.yaml'):
    with open(config) as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data

def get_hash():
    alphabet = string.ascii_letters + string.digits 
    rand_hash = ''.join(secrets.choice(alphabet) for i in range(8)) 
    return rand_hash

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

def compare_sets_common(label_dict, image_dict):
    labels_names = set(label_dict.keys())
    images_names = set(image_dict.keys())

    dif_1 = list(labels_names - images_names)
    dif_2 = list(images_names - labels_names)

    if dif_1!=[] or dif_2!=[]:
        print(f"difference is: {dif_1+dif_2}")
    else :
        print("no difference in images and labels")
    
    common_items = labels_names & images_names
    print(f"Amount")
    print(f"labels: {len(labels_names)}")
    print(f"images: {len(images_names)}")
    print(f"common item: {len(common_items)}")
    
    return common_items

def create_path_out(path_out):
    dst_labels = os.path.join(path_out,"labels")
    dst_imgs = os.path.join(path_out,"images")
    if not os.path.isdir(dst_labels):
        os.mkdir(dst_labels) 
    if not os.path.isdir(dst_imgs):
        os.mkdir(dst_imgs)
    return dst_labels, dst_imgs

def src_dst_move(path_in,
                 path_out,
                 slovr,
                 item,
                 type_dir,
                 not_oppened_imgs_OBJ):


    ext = slovr[item]
    SrcDst_name = f"{item}{ext}"
    src_path = os.path.join(path_in, type_dir, SrcDst_name)
    
    ## cheking image by oppening it
    if type_dir=="images" and cv.imread(src_path, 0) is None:
        not_oppened_imgs_OBJ.append(SrcDst_name)
    
    dst_path = os.path.join(path_out, type_dir, SrcDst_name)
    
    shutil.move(src_path, dst_path)
    
    return src_path, dst_path, not_oppened_imgs_OBJ

    

def mover_ImgsLabls(path_in,
            path_out,
            labels_dict,
            images_dict,
            common_items,
            transfer_percentage):
    
    dst_labels, dst_imgs =  create_path_out (path_out) 
    not_oppened_imgs=[]


    amount_selected = int(transfer_percentage*len(common_items))
    moved_items = random.sample(list(common_items), amount_selected)
    print(f"Moved amount: {amount_selected} items ({transfer_percentage}%) of {len(common_items)}")
    
    for item in tqdm(moved_items):
        # hash_name = secrets.token_urlsafe(6)

        src_img, dst_img, not_oppened_imgs = src_dst_move( path_in, 
                                         path_out, 
                                         images_dict, 
                                         item,  
                                         "images",
                                         not_oppened_imgs)
        
        src_label, dst_label, _ = src_dst_move(path_in,
                                         path_out,
                                         labels_dict, 
                                         item, 
                                         "labels",
                                         None)
        
    print(f"not_oppened_imgs: {not_oppened_imgs}")
    print(f"Task has done! 🎉")
        
        