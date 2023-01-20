def resize_with_pad(img: np.array, new_size):
    old_ratio = img.shape[1]/img.shape[0]
    new_ratio = new_size[0]/new_size[1]

    if(new_ratio < old_ratio):
        new_h = new_size[0]
        new_w = int(new_h / old_ratio)
    else:
        new_w = new_size[1]
        new_h = int(new_w * old_ratio)

    img = cv.resize(img, (new_h, new_w))

    f = np.zeros((new_size[1],new_size[0],3),np.uint8)
    shift_x = int((new_size[1] - img.shape[0])/2)
    shift_y = int((new_size[0] - img.shape[1])/2)
    f[shift_x:img.shape[0]+shift_x,shift_y:img.shape[1]+shift_y] = img
    return f