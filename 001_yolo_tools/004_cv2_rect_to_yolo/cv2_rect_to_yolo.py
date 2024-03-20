from typing import List

def cv2_rect_to_yolo(x1,x2,y1,y2, w_size, h_size):
    w=(x2-x1)/w_size
    h=(y2-y1)/h_size
    x = x1/w_size + w/2
    y = y1/h_size + h/2

    return x,y,w,h


def write_yolo(list_yolo_labels:List[List[int]], 
               path:str):
    """
    list_yolo_labels =[ [clas, x, y, w, h], [clas, x, y, w, h] ] = List[  List[int, int, int, int, int]  ]
    """
    str_data = ""
    for i in list_yolo_labels: # clas, x, y, w, h
        i=" ".join(map(str, i))
        str_data+=f"\n{i}"

    str_data=str_data.strip()+"\n"
    with open(path, "w") as text_file:
        text_file.write(str_data)
    print("file writed")

