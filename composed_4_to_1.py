import os
import cv2
import numpy as np

from natsort import natsorted, ns
from tqdm import tqdm  

initial_dir="/home/msi/Документы/project/detect_guns/data/20_Ivan_postanovka/"

frame_width,frame_height=1920,1080

trhsld1="output_1_trshld0,1/"
trhsld3="output_1_trshld0,3/"
trhsld5="output_1_trshld0,5/"
trhsld7="output_1_trshld0,7/"

out_composed="composed/"



# Put text
font = cv2.FONT_HERSHEY_SIMPLEX
  
# org
org = (50, 50)
  
# fontScale
fontScale = 1
   
# Blue color in BGR
color = (255, 0, 0)
  
# Line thickness of 2 px
thickness = 2
   
fourcc = cv2.VideoWriter_fourcc(*'H264')

for i in tqdm(natsorted(os.listdir(initial_dir+trhsld1))):
    video1 = cv2.VideoCapture(initial_dir+trhsld1+i)  #  Захватываем фрагмент видеофайла
    video3 = cv2.VideoCapture(initial_dir+trhsld3+i)  #  Захватываем фрагмент видеофайла
    video5 = cv2.VideoCapture(initial_dir+trhsld5+i)  #  Захватываем фрагмент видеофайла
    video7 = cv2.VideoCapture(initial_dir+trhsld7+i)  #  Захватываем фрагмент видеофайла

    fps= int(video1.get(cv2.CAP_PROP_FPS))
    out = cv2.VideoWriter(initial_dir+out_composed+i,cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width,frame_height))  # cv2.VideoWriter_fourcc('M','J','P','G')

    currentframe = 0
    while(True):

        video1.set(1, currentframe) # установить каждый 25 кадр 
        video3.set(1, currentframe) # установить каждый 25 кадр 
        video5.set(1, currentframe) # установить каждый 25 кадр 
        video7.set(1, currentframe) # установить каждый 25 кадр 

        # чтение из кадра
        ret1,frame1 = video1.read()
        ret3,frame3 = video3.read()     
        ret5,frame5 = video5.read()     
        ret7,frame7 = video7.read()     
        if ret1:
            dim = (int(frame_width/2), int(frame_height/2))
            # resize image
            frame1 = cv2.resize(frame1, dim, interpolation = cv2.INTER_AREA)
            frame3 = cv2.resize(frame3, dim, interpolation = cv2.INTER_AREA)
            frame5 = cv2.resize(frame5, dim, interpolation = cv2.INTER_AREA)
            frame7 = cv2.resize(frame7, dim, interpolation = cv2.INTER_AREA)


            frame1 = cv2.putText(frame1, 'trhsld=0,1', org, font,fontScale, color, thickness, cv2.LINE_AA)
            frame3 = cv2.putText(frame3, 'trhsld=0,3', org, font,fontScale, color, thickness, cv2.LINE_AA)
            frame5 = cv2.putText(frame5, 'trhsld=0,5', org, font,fontScale, color, thickness, cv2.LINE_AA)
            frame7 = cv2.putText(frame7, 'trhsld=0,7', org, font,fontScale, color, thickness, cv2.LINE_AA)



            l1 = np.concatenate((frame1, frame3), axis=1)
            l2 = np.concatenate((frame5, frame7), axis=1)
            l3 = np.concatenate((l1 , l2 ), axis=0)

            out.write(l3)

            # cv2.imwrite(initial_dir +"img/"+ str(currentframe)+".jpg", l3)

            # увеличение счетчика, чтоб бежать по видео
            currentframe += 1
            print('Completed frame: {}'.format(currentframe), end='\r')
        else:
            break
    # Освободить все пространство и окна, как только сделано
    video1.release()
    video3.release()
    video5.release()
    video7.release()
    out.release()