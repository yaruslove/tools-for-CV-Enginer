import glob
import os
import cv2
import textwrap
import argparse



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Cut bbox yolo',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''Cut bbox yolo from txt labels'''))

    parser.add_argument('-l', '--labels_pth', type=str, required=True)
    parser.add_argument('-i','--imgs_pth', type=str, required=True)
    parser.add_argument('-o', '--out_pth', type=str, required=True) # how often take frame

    args = parser.parse_args()
    print(args)

    labels_pth=args.labels_pth
    imgs_pth=args.imgs_pth
    out_pth=args.out_pth


    labels_pth=glob.glob(f"{labels_pth}*.txt")

    for cur_lab in labels_pth: 
        name_file=os.path.basename(cur_lab)
        name_file=name_file[:name_file.rfind(".")]
        
        for img_name in os.listdir(imgs_pth):
            if (img_name).startswith(name_file+"."):
                break
        
        img = cv2.imread(os.path.join(imgs_pth,img_name))
        h,w,_ =img.shape
        
        f = open(cur_lab,'r')
        f = f.read()
        f=f.strip().split("\n")
        for idx,i in enumerate(f):
            cl,x1,y1,x2,y2=i.split(" ")
            cl,x1,y1,x2,y2=float(cl),float(x1),float(y1),float(x2),float(y2)
            # print(i)
            xstrt=int((x1-x2/2)*w)
            xend=int((x1+x2/2)*w)
            ystrt=int((y1-y2/2)*h)
            yend=int((y1+y2/2)*h)
            tmp_img=img[ystrt:yend, xstrt:xend]
            tmp_outpath=os.path.join(out_pth, name_file+".jpg")
            cv2.imwrite(tmp_outpath, tmp_img)


print("\n")
print("Program finished!")