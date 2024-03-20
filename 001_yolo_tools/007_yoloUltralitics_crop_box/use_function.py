from infernce_crop_YOLOv8 import Infernce_crop_YOLOv8

path_weight = "/home/yaroslav/Documents/001_Projects/tomato/003_train_script/006_yolo_det/train3/weights/best.pt"

path_in = "/home/yaroslav/Documents/001_Projects/tomato/001_raw_data/010_data_greenhouse_20_12_23/raw_data/luxonis/from_far_side_car_octopus/"
path_out = "/home/yaroslav/Documents/001_Projects/tomato/001_raw_data/010_data_greenhouse_20_12_23/raw_data/luxonis/cropp/from_far_side_car_octopus/"


inference_crop = Infernce_crop_YOLOv8(path_weight)

inference_crop.inference_crop(path_in, path_out)