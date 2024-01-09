import os
import pandas as pd

import argparse
import textwrap

import random
import shutil
import glob


'''
python3 001_recollect_dataset.py --src-csv "/home/arch/Документы/project/angel/incass_classification/dataset/trains/003_train/train_set.csv" \
--src-data /home/arch/Документы/project/angel/incass_classification/dataset/prepared_data_001/ \
--dst-data /home/arch/Документы/project/angel/incass_classification/dataset/trains/003_train/tmp_collect/
'''


def copyFiles2dir(lst_imgs, dst):
    os.makedirs(dst, exist_ok=True)
    for img_pth in lst_imgs:
        shutil.copy(img_pth, dst)

def recollect_dataset(dframe_csv,src_data,dst_data):
    for main_dir, row in dframe_csv.iterrows():
        current_main_dir=os.path.join(src_data, main_dir, "sorted")
        for name_class, cell_value  in zip(row.index,row):
            current_class_dir = os.path.join(current_main_dir, name_class)
            if not os.path.exists(current_class_dir):
                continue
            all_dir_sampels = glob.glob(f"{current_class_dir}/*")
            selected_imgs = random.sample(all_dir_sampels, cell_value)
            curent_dst=os.path.join(dst_data,main_dir,name_class)
            
            copyFiles2dir(selected_imgs,curent_dst)
    print(f"Process done!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Classifier training program',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                         Data dir example:
                                            data/ <-- path src to this dir [--data] argument
                                            ├──001_first_image_set/
                                            │  └─sorted/
                                            │     ├──<class_1>
                                            │     ├──<class_2>
                                            │     └──<class_N>
                                            │
                                            │
                                            │
                                            ├──002_second_image_set/
                                            │  └─sorted/
                                            │     ├──<class_1>
                                            │     ├──<class_2>
                                            │     └──<class_N>
                                            │
                                            ........
                                            ........
                                            │
                                            └──XXX_N_image_set/
                                               └─sorted/
                                                  ├──<class_1>
                                                  ├──<class_2>
                                                  └──<class_N>

                                         '''))
    # Get aruments  
    parser.add_argument('--src-csv', type=str, required=True)
    parser.add_argument('--src-data', type=str, required=True, help='path with initiall data with files')
    parser.add_argument('--dst-data', type=str, required=True, help='path to create dir and copy fiels')


    args = parser.parse_args()

    src_csv=args.src_csv
    src_data=args.src_data
    dst_data=args.dst_data


    df_csv = pd.read_csv(src_csv, delimiter=";",index_col="Name")
    recollect_dataset(df_csv, src_data, dst_data)