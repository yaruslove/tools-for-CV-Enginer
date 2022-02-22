## This repo for cutting objects from images to separate folder.
Labels for cutting get from YOLO labels .txt files

![](bbox_cut.png)


```
python3 cut_yolo_bbox.py \
--labels_pth '/Volumes/labels/' \
--imgs_pth '/Volumes/images/' \
--out_pth '/Volumes/cutted_out/'
```

```
--labels_pth   path where located txt YOLO files  
--imgs_pth     path where located images files  
--out_pth      path where will save croped images
```