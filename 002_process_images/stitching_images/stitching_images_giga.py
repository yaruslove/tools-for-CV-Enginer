import cv2
from matplotlib import pyplot as plt
import numpy as np

def stitch_images(image1, image2, method="SIFT"):
    # Загрузка изображений
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)
    
    # Преобразование цветовых пространств
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    if method == "SIFT":
        # Поиск ключевых точек с помощью SIFT
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        # Создание BFMatcher
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Фильтрация дубликатов
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append([m])

        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        pts = np.float32([[0, 0], [img1.shape[1], 0], [0, img1.shape[0]], [img1.shape[1], img1.shape[0]]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        # Изменение размера для отображения
        h, w = img2.shape
        trapezoid = np.max((dst[:, 1, 0] - dst[:, 0, 0]), (dst[:, 3, 0] - dst[:, 2, 0])) / 2
        center = (np.min((dst[:, 0, 0] + dst[:, 1, 0]) / 2, (dst[:, 2, 0] + dst[:, 3, 0]) / 2), h / 2)
        pts = np.float32([[0, 0], [w, 0], [trapezoid, h], [w - trapezoid, h]])
        M = cv2.getPerspectiveTransform(dst, pts)
        result = cv2.warpPerspective(img2, M, (int(w), int(h)))
    else:
        # Ваш метод
        pass

    return result

# Загрузка изображений
image1 = "/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/002_tops/001_raw_data/009_joined_20_11_24_TkPodmoskovie_video/001_raw_vids/002_tomatos/IMG_2913_new_start/IMG_2913_new_start_10.jpg"
image2 = "/Volumes/Orico/projetcs_sbs/001_green-houses/001_DS_models/002_tops/001_raw_data/009_joined_20_11_24_TkPodmoskovie_video/001_raw_vids/002_tomatos/IMG_5823_new_start/IMG_5823_new_start_10.jpg"

# Сшивание изображений
stitched_image = stitch_images(image1, image2, method="SIFT")

# Показ результата
plt.figure(figsize=(15, 15))
plt.axis("off")
plt.title("Stitched Image")
plt.imshow(stitched_image)
plt.show()