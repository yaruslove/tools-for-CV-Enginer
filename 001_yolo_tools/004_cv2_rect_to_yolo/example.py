import numpy as np
import cv2
from cv2_rect_to_yolo import cv2_rect_to_yolo, write_yolo

# array x1, x2, y1, y2
array_cats = np.array([  
[35, 299, 175, 469],
[265, 497, 182, 460],
[457, 665, 28, 424]])

w_size = 701
h_size = 514
cl=0

path_img = "./labels/cats.jpeg"
path_yolo_label = "./labels/cats.txt"
img_np=cv2.imread(path_img)

list_yolo_labels=[]
cl=0
for x1, x2, y1, y2 in array_cats:
    x,y,w,h = cv2_rect_to_yolo(x1,x2,y1,y2, w_size, h_size)
    list_yolo_labels.append([cl, x, y, w, h])
    
write_yolo(list_yolo_labels, path_yolo_label)





   