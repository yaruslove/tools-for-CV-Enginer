from ultralytics import YOLO
import os
import glob
import math

from PIL import Image
from tqdm import tqdm



class Infernce_crop_YOLOv8:
    def __init__ (self, path_weight):
        # Load a model
        self.model = YOLO(path_weight)  # pretrained YOLOv8n model

    def inference_crop(self, path_in, path_out):
        self.path_in = path_in
        self.path_out = path_out

        batch_size=8
        list_imgs = glob.glob(f"{self.path_in}{'/*'}")
        lenght_files=len(list_imgs)
        amount_batches = math.ceil(lenght_files/batch_size)


        for n_batch in tqdm(range(amount_batches)): # This loop to put batches into model
            batch_files = list_imgs[n_batch*batch_size:(n_batch+1)*batch_size]
            results = self.model( batch_files, conf=0.5, show_conf = True, show_labels =True, line_width =1)  # return a list of Results objects
            self.loop_crop_class2image(results)


    def loop_crop_class2image(self, results):
        for r in results:
            orig_img = r.orig_img
            classes = r.names
            path_img = os.path.basename(r.path)
            counter = 0
            for cl, conf, xyxy in zip(r.boxes.cls, r.boxes.conf, r.boxes.xyxy):
                if cl==0 : # and conf>0.55
                    x1,y1,x2,y2 = xyxy.detach().cpu().numpy().astype(int)
                    crp_img = orig_img[ y1:y2, x1:x2] 
                    crp_img = Image.fromarray(crp_img[..., ::-1])  # RGB-order PIL image
                    # Conf
                    conf = round(float(conf), 2)
                    # Create new name for crop image
                    insertion = f"{counter}_{conf}"
                    crop_name = self.insert_pth (path_img, insertion)
                    
                    is_saved = crp_img.save(os.path.join(self.path_out, crop_name)) 
                    counter+=1 


    def insert_pth (self, path_img, insertion):
        n_point =  path_img.rfind('.')
        name = path_img[:n_point]
        ext = path_img[n_point:]
        changed_name = f"{name}_{insertion}{ext}"
        return changed_name
