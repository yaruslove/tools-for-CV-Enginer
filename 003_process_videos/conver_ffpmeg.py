import os
import subprocess

path_in='/home/msi/Документы/project/detect_guns/data/20_Ivan_postanovka/composed/'
path_out='/home/msi/Документы/project/detect_guns/data/20_Ivan_postanovka/composed_264/'

for i in os.listdir(path_in):
    name_out=i.replace(" ", "")
    process = subprocess.Popen(["ffmpeg", "-i", f"{path_in}/{i}", "-vcodec", "libx264", f"{path_out}/{i}"], stdout=subprocess.PIPE)
    # process = subprocess.Popen(["ffmpeg", "-vcodec", "mpeg4", "-b:v", "2000k", "-qscale:v", "8", "-acodec", "aac", "-ac", "2", "-async", "1", "-strict", "experimental", f"{path_out}/{name_out}", "-threads", "8", "-i", f"{path_in}/{i}"], stdout=subprocess.PIPE)
    # process = subprocess.Popen(["ffmpeg", "-vcodec", "mpeg4", "-minrate", "1500k", "-maxrate", "3000k", "-bufsize", "2000k", "-qscale:v", "5", "-acodec", "aac", "-ac", "2", "-async", "1", "-strict", "experimental", f"{path_out}/{name_out}", "-threads", "8", "-i", f"{path_in}/{i}"], stdout=subprocess.PIPE)

    # ffmpeg -vcodec mpeg4 -b:v 7561k -qscale:v 2 -acodec aac -ac 2 -async 1 -strict experimental ./video_fixed.mp4 -threads 0 -i damage_file.mp4
    # process = subprocess.Popen(["ffmpeg", "-vcodec", "mpeg4", "-minrate", "1500k", "-maxrate", "3000k", "-bufsize", "2000k", "-qscale:v", "6", "-acodec", "aac", "-ac", "2", "-async", "1", "-strict", "experimental", f"{path_out}/{name_out}", "-threads", "16", "-i", f"{path_in}/{i}"], stdout=subprocess.PIPE)

    code = process.wait()
    data = process.communicate()[0]

