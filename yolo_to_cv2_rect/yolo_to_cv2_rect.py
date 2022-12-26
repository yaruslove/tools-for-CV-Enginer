str_yolo = "32 0.262,0.7878 0.314 0.385"

def yolo_to_cv2_rect(str_yolo,h,w):
    x1 = int( float(str_v.split(' ')[1]) * w )
    y1 = int( float(str_v.split(' ')[2]) * h )
    xw = int( float(str_v.split(' ')[3]) * w /2)
    yw = int( float(str_v.split(' ')[4]) * h /2)
    #make x1,y1, x2,y2

    start_point = (x1 - xw, y1 - yw )
    end_point   = (x1 + xw, y1 + yw )
    return start_point,start_point
