def resize_with_pad(image: np.array, 
                    w:int,
                    h:int ) -> np.array:
    black_vector = (0, 0, 0)
    blk_blnk=np.full((*(h,w), len(black_vector)), black_vector).astype(np.uint8)
    w_src,h_src,_=image.shape
    dst_ratio=h/w
    src_ratio=h_src/w_src
    
    if src_ratio>=dst_ratio:
        h_tmp=h
        w_tmp=int(h_tmp*src_ratio)
        image=cv.resize(image, (w_tmp,h_tmp), interpolation = cv.INTER_AREA)
        pad_half=int((w-w_tmp)/2)
        blk_blnk[0:h_tmp,pad_half:int(pad_half+w_tmp)] = image
    if src_ratio<dst_ratio:
        w_tmp=w
        h_tmp=int(w_tmp*src_ratio)
        image=cv.resize(image, (w_tmp,h_tmp), interpolation = cv.INTER_AREA)
        pad_half=int((h-h_tmp)/2)
        blk_blnk[pad_half:int(pad_half+h_tmp),0:w_tmp] = image

    return blk_blnk