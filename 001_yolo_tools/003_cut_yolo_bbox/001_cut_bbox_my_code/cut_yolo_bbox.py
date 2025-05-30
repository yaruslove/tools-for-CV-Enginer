import glob
import os
import cv2
import textwrap
import argparse
from tqdm import tqdm

class StoreDictKeyPair(argparse.Action):
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values.split(","):
             k,v = kv.split("=")
             k=int(k)
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Cut bbox yolo',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''Cut bbox yolo from txt labels'''))

    parser.add_argument('-l', '--labels_pth', type=str, required=True)
    parser.add_argument('-i','--imgs_pth', type=str, required=True)
    parser.add_argument('-o', '--out_pth', type=str, required=True) # how often take frame
    parser.add_argument('-c','--classes', action=StoreDictKeyPair, metavar='KEY1=VAL1,KEY2=VAL2...') #, dest='my_dict'

    args = parser.parse_args()
    print(args)

    classes=args.classes
    labels_pth=args.labels_pth
    imgs_pth=args.imgs_pth
    out_pth=args.out_pth


    labels_pth=glob.glob(f"{labels_pth}/*.txt")

    no_image=[]

    # make dirs with classes
    for pth_cl in classes.values():
        pth_cl=os.path.join(out_pth, pth_cl)
        if not os.path.exists(pth_cl):
            os.makedirs(pth_cl)

    pbar = tqdm(labels_pth)
    name_file=""
    for cur_lab in pbar:
        if cur_lab.endswith("classes.txt"):
            continue
        name_file=os.path.basename(cur_lab)
        pbar.set_postfix({'num_vowels': name_file})
        # print(name_file)
        name_file=name_file[:name_file.rfind(".")]
        
        trig=0 # Останеться 0 если есть txt но нет image
        for img_name in os.listdir(imgs_pth):
            if (img_name).startswith(name_file+".") and not (img_name).endswith(name_file+".txt"):
                trig=1
                break
             
        if  trig==0:      
            no_image.append(name_file)
            continue
        
        img = cv2.imread(os.path.join(imgs_pth,img_name))
        h,w,_ =img.shape
        
        f = open(cur_lab,'r')
        f = f.read()
        if len(f)<3:
            continue
        f=f.strip().split("\n")
        
        for idx,i in enumerate(f):

            i=[float(j) for j in i.strip().split(" ")]
            cl,x1,y1,x2,y2=i[0],i[1],i[2],i[3],i[4]
            # cl,x1,y1,x2,y2=float(cl),float(x1),float(y1),float(x2),float(y2)
            xstrt=int((x1-x2/2)*w)
            xend=int((x1+x2/2)*w)
            ystrt=int((y1-y2/2)*h)
            yend=int((y1+y2/2)*h)
            tmp_img=img[ystrt:yend, xstrt:xend]

            if int(cl) not in classes.keys():
                continue



            tmp_outpath=os.path.join(out_pth, classes[int(cl)],name_file+"_"+str(idx)+".png")

            cv2.imwrite(tmp_outpath, tmp_img)


print("Amount exist txt no image = ",str(len(no_image)))
print("List txt no image: ",no_image)
print("\n")
print("Program finished!")
