import cv2 as cv
import numpy as np
import os
import textwrap
import argparse
import math
from tqdm import tqdm

def rotation(image, angleInDegrees):
    h, w = image.shape[:2]
    img_c = (w / 2, h / 2)

    rot = cv.getRotationMatrix2D(img_c, angleInDegrees, 1)

    rad = math.radians(angleInDegrees)
    sin = math.sin(rad)
    cos = math.cos(rad)
    b_w = int((h * abs(sin)) + (w * abs(cos)))
    b_h = int((h * abs(cos)) + (w * abs(sin)))

    rot[0, 2] += ((b_w / 2) - img_c[0])
    rot[1, 2] += ((b_h / 2) - img_c[1])

    outImg = cv.warpAffine(image, rot, (b_w, b_h), flags=cv.INTER_LINEAR)
    return outImg


parser = argparse.ArgumentParser(prog='Grab frame from video/videos',
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                description=textwrap.dedent('''grab frame from video/videos and save them into fold/folders'''))

parser.add_argument('-s', '--src', type=str, required=True)
parser.add_argument('-d','--dst', type=str, required=True)
parser.add_argument('-r', '--rotate-angle', type=int, default=25) # how often take frame

args = parser.parse_args()
print(args)


src=args.src
dst=args.dst
rotate_angle=args.rotate_angle

for pth_image in tqdm(os.listdir(src)):
    print(f"{pth_image}")
    img_np = cv.imread(os.path.join(src,pth_image))
    img_np=rotation(img_np, rotate_angle)

    pth_image_save=os.path.join(dst,pth_image)
    cv.imwrite(pth_image_save, img_np)
