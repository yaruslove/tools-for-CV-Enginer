import os
from delete_labels import delete_labels

path_dirs ="/home/yaroslav/Documents/001_Projects/005_car_number/data/001_raw_data/001_plates/"

for i in os.listdir(path_dirs):
    print(i)
    path_in = os.path.join(path_dirs, i)

    delete_labels(path_in)
    print(f"\n\n")