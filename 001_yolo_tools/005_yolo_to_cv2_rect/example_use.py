import cv2
from yolo_to_cv2_rect import yolo_to_cv2_rect


path_yolo_label = "./labels/cats.txt"
path_image = "./labels/cats.jpeg"

with open(path_yolo_label) as f:
    lines = f.readlines()

# print(lines)

w_size = 701
h_size = 514

img_np=cv2.imread(path_image)

for label_str in lines:
    # print(label_str.strip())
    label_str=label_str.strip()
    # pass
    x1, x2, y1, y2 = yolo_to_cv2_rect(label_str, w_size, h_size)
    print(x1, x2, y1, y2)

    cv2.imshow('image',img_np[y1:y2, x1:x2])
    cv2.waitKey(0)


