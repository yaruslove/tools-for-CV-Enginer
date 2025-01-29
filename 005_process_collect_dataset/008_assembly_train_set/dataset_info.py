import os
import pandas as pd
from natsort import natsorted, ns


from utils.tools import remove_ds_store, get_yaml_config, prep_columns, create_df_asis, count_totalsum
from utils.recount_distribute_sum import recount_distribute_sum
from utils.save_trainset import save_trainset

## Read config
config = get_yaml_config("configs/conf_dataset_info.yaml")


# Config variables
path_data = config["path_data"]
path_final_data = config["path_final_data"]
path_out_excel = config["path_out_excel"]
name_excel_file = config["name_excel_file"]
classes = config["classes"]
classes = list(map(str, classes))
print(f"classes {classes}")


### add columns names and sorted classes
columns = prep_columns(classes)


## Remove .DS_Store
remove_ds_store(path_data)

## List sources
list_sources = os.listdir(path_data)
list_sources = natsorted(list_sources, alg=ns.IGNORECASE) 

## Create df_asis for ALL sources
df_asis = create_df_asis(columns, list_sources, path_data, path_final_data, classes)
print(f"As is initial data")


### Count totalsum
df_asis = count_totalsum(df_asis)
print(df_asis)

## Save df_asis to excel
df_asis.to_csv(os.path.join(path_out_excel, name_excel_file), index=False)

print(f"\n\nData saved to excel, \nScript finished!")