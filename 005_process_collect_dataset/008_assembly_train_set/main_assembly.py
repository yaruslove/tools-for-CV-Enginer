import os
import pandas as pd

from utils.tools import remove_ds_store, get_yaml_config, prep_columns, create_df_asis
from utils.recount_distribute_sum import recount_distribute_sum
from utils.save_trainset import save_trainset

## Read config
config = get_yaml_config("configs/conf_assemble.yaml")

# Config variables
path_data = config["path_data"]
path_final_data = config["path_final_data"]
list_sources = config["list_sources"]
amount_in_class = config["amount_in_class"]
path_out = config["path_out"]
name_dir = config["name_dir"]
classes = config["classes"]
classes = list(map(str, classes))
print(f"classes {classes}")


### add columns names and sorted classes
columns = prep_columns(classes)


## Remove .DS_Store
remove_ds_store(path_data)

## Create df_asis
df_asis = create_df_asis(columns, list_sources, path_data, path_final_data, classes)
print(f"As is initial data")
print(df_asis)

## Recount distribute sum
df_redistribute = recount_distribute_sum(df_asis, amount_in_class)

print(f"\n\n\n")
print(f"Redistribute data")
print(df_redistribute)


## Save data
save_trainset(df_redistribute, path_data, path_final_data, path_out, name_dir, classes)

