### Script to rename files: images and labels

initially you need tweak *config.yaml* 

```
path_in: "/Users/Vasya/val"
path_out: "/Users/Vasya/val_rename"
prefix: 004_Zaharov
```

INPUT_DATA:
```
    val/
        │
        ├── classes.txt
        │
        ├── images
        │   ├── КПП 5 Камера 01 (31-08-2023_18-15-30.668).jpg
        │   ├── CamRTSP%$ 5 Камера 01 (29-08-2023_87-15-30.668).png
        │   ├── .....
        │   └── 29163987.jpg
        │
        └── labels
            ├── КПП 5 Камера 01 (31-08-2023_18-15-30.668).txt
            ├── CamRTSP%$ 5 Камера 01 (29-08-2023_87-15-30.668).txt
            ├── .....
            └── 29163987.jpg
```

OUTPUT_DATA:
```
    val_rename/
        │
        ├── classes.txt
        │
        ├── images
        │   ├── 004_Zaharov_0_7bdppvT9.jpg
        │   ├── 004_Zaharov_1_O9j0ZDXq.png
        │   ├── .....
        │   └── 004_Zaharov_990_im8hqO5v.jpg
        │
        └── labels
            ├── 004_Zaharov_0_7bdppvT9.txt
            ├── 004_Zaharov_1_O9j0ZDXq.txt
            ├── .....
            └── 004_Zaharov_990_im8hqO5v.txt
```

**Run script**
```
python3 rename_imgs_datasets.py
```
