from utils import  read_yaml
import pandas as pd
from utils import copy_files

def split4train(path_in_raw, 
                path_out_train,
                csv_file):
    
    df = pd.read_csv(csv_file, sep='\t')

    sets=list(df.columns)
    print(sets)
    sets.remove('names')

    list(df[df["train"]=="+"].names)

    for s in sets: # sets = ["train","val"]
        list_dirs = list(df[df[s]=="+"].names)
        for dir_name in list_dirs:
            copy_files(dir_name, s, path_in_raw, path_out_train)

    print(f"Task has done! 🎉")




data = read_yaml(config='config.yaml')
print(data)
path_in_raw = data["path_in_raw"]
path_out_train = data["path_out_train"]
csv_file = data["csv_file"]

split4train(path_in_raw, 
            path_out_train,
            csv_file)

