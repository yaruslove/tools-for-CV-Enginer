import os
import cv2
import textwrap
import argparse



if __name__ == '__main__':
    def grab_frame(src_loc,dst_loc,rate_loc,base_name_file):
        video = cv2.VideoCapture(src_loc)  #  Захватываем фрагмент видеофайла
        currentframe = 0

        while(True):
            video.set(1, currentframe) # чтение кадров
            ret,frame = video.read()     
            if ret: # если видео еще осталось, продолжайте создавать изображения
                name_out=os.path.join(dst_loc, base_name_file+'_'+str(int(currentframe/rate_loc)) + '.jpg')
                cv2.imwrite(name_out, frame) # запись извлеченных изображений в папку
                currentframe += rate_loc
            else:
                break
        video.release() # открпеить видеофайл

    parser = argparse.ArgumentParser(prog='Grab frame from video/videos',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''grab frame from video/videos and save them into fold/folders'''))

    parser.add_argument('-s', '--src', type=str, required=True)
    parser.add_argument('-d','--dst', type=str, required=True)
    parser.add_argument('-r', '--rate', type=int, default=25) # how often take frame

    args = parser.parse_args()
    print(args)


    src=args.src
    dst=args.dst
    rate=args.rate

    if os.path.isfile(src): # Если 1 видеофайл
        # Получеие имени файла без расширения
        base_name_file=os.path.basename(src)
        print("Processing: "+base_name_file)

        base_name_file=base_name_file[:base_name_file.rfind(".")] 
        grab_frame(src,dst,rate,base_name_file)
    elif os.path.isdir(src): # Если несколько видеофайлов
        for i in os.listdir(src):
            vid_formats=('.mp4', '.avi', '.MOV', '.asf')   
            if i.endswith(vid_formats) and not i.startswith("."):
                print("Processing: "+i)
                src_loc=os.path.join(src,i)
                base_name_file=i[:i.rfind(".")]
                dst_loc=os.path.join(dst,base_name_file)
                if not os.path.exists(dst_loc):
                    os.makedirs(dst_loc)

                grab_frame(src_loc,dst_loc,rate,base_name_file)