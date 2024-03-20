str_yolo = "32 0.262,0.7878 0.314 0.385"

def yolo_to_cv2_rect(str_yolo, w_res, h_res):
    # parse
    cl, x_cent_rel, y_cent_rel, w_rel, h_rel = str_yolo.split(' ')
    # relative value to abs
    x_cent_abs = int( float (x_cent_rel) * w_res )
    y_cent_abs = int( float (y_cent_rel) * h_res )
    w_abs_half = int( float(w_rel) * w_res /2)
    h_abs_half = int( float(h_rel) * h_res /2)

    x1 = x_cent_abs - w_abs_half
    x2 = x_cent_abs + w_abs_half
    y1 = y_cent_abs - h_abs_half
    y2 = y_cent_abs + h_abs_half

    return x1, x2, y1, y2