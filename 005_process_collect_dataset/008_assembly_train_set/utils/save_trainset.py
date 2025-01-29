import os
import random
import shutil
from tqdm import tqdm
from utils.tools import safly_create_dir, read_data, get_only_directories


def create_dir_by_class(path_out, classes):
    # Create path out
    safly_create_dir(path_out)

    # Create dir by class
    for cl_name in classes:
        path_class = os.path.join(path_out, cl_name)
        safly_create_dir(path_class)


def copy_images(path_src, path_dst, random_select_images):
    for img_name in random_select_images:
        shutil.copy(os.path.join(path_src, img_name), os.path.join(path_dst, img_name))



def save_trainset(df_redistribute, path_data, path_final_data, path_out, name_dir, classes):

    ## Create dir by class
    path_out = os.path.join(path_out, name_dir)
    create_dir_by_class(path_out, classes)
    

    list_sources = df_redistribute['name']

    print("########################")
    print(f"Assemble dataset, copying images...")
    print("........................")
    for source in tqdm(list_sources): # DIRS: 001_AM, 002_ECO, 003_iphone
        path_src = os.path.join(path_data, source)
        path_classes = read_data(path_src, path_final_data)
        if path_classes is None:
            continue

        list_classes = get_only_directories(path_classes)

        for cl_name in list_classes: # classes 1, 2, 3, 4, 5, 6, 7
            path_images = os.path.join(path_classes, cl_name)
            
            list_imgs = os.listdir(path_images)
            
            ### Get amount images in class
            value = df_redistribute.loc[df_redistribute['name'] == source, cl_name].iloc[0]
            path_dst = os.path.join(path_out, cl_name)

            ### Paths
            # SRC - path_images 
            # DST - path_dst 

            ### Random select images
            random_select_images = random.sample(os.listdir(path_images), value)
            # print(f"source {source}")
            # print(f"class {cl_name}")
            # print(f"random_select_images {len(random_select_images)}")

            ### Copy images
            copy_images(path_images, path_dst, random_select_images)

            ### Save df_redistribute as csv
            df_redistribute.to_csv(os.path.join(path_out, "df_redistribute.csv"), index=False)


    


    




            







    