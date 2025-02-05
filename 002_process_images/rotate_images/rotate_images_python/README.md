## Python cv2 rotate images in dir

now it just working for 180° degree, if it 90° it will cropp the images

```
python3 rotate_cv2.py \
--src /home/arch/Documents/project/angel/image_classification/dataset/prepare_data/009_Postanovka/raw_out_frames/IMG_3483+ \
--dst /home/arch/Documents/project/angel/image_classification/dataset/prepare_data/009_Postanovka/raw_out_frames/IMG_3483 \
--rotate-angle 180
```


```
python3 rotate_cv2.py \
--src /Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/002_tops/001_tops_detection/001_raw_data/011_ECO_C_january_2025/002_raw_data_img/out_freq5_clear/IMG_2241 \
--dst /Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/002_tops/001_tops_detection/001_raw_data/011_ECO_C_january_2025/002_raw_data_img/out_freq5_clear/IMG_2241_rotated \
--rotate-angle 270
```