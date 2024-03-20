import yaml
import os
import shutil



def read_yaml(config='config.yaml'):
    with open(config) as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data


# def copyDir2Dir()

def copy_files(dir_name, s, path_in_raw, path_out_train):
    src_labels = os.path.join(path_in_raw, dir_name, "labels")
    src_images = os.path.join(path_in_raw, dir_name, "images")

    dst_labels = os.path.join(path_out_train, s, "labels")
    dst_images = os.path.join(path_out_train, s, "images")

    for ful_path in [dst_labels, dst_images]:
        if not os.path.exists(ful_path):
            os.makedirs(ful_path)


    shutil.copytree(src_labels, dst_labels, dirs_exist_ok=True)
    shutil.copytree(src_images, dst_images, dirs_exist_ok=True)


