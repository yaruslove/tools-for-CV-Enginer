## Скрипт заменяет указанные yolo-лейблы в txt файлах по словарю --zamena 0=1,2=3,7=10.



```
python3 change_yolo_classes.py \
--labels_pth /Volumes/test/ \
--zamena 0=1,2=3,7=10
```

```
python3 change_yolo_classes.py \
--labels_pth /Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/002_tops/001_tops_detection/001_raw_data/007_Dima_20_11_24_TkPodmoskovie_video/005_verified_annotation/001_labeled_26_12_24_Olga/project_remaped/labels \
--zamena 0=3,1=1,2=0,3=2
```

Где --zamena 0=1,2=3,7=10    0 - это старое значение земениться на 1
старое значение 2 замениться на 3
7 замениться на 10

