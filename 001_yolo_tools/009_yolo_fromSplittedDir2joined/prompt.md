Напиши скрипт python который создаст нужные папки и в правильном порядке скопирует данные. На вход скрипту подается четыре параметра.
src_imgs
src_labels
src_classes
joined

Данные ппапки имеют такую структуру

src_imgs/
  dir1/
    image1.jpg
    image2.jpg
  dir2/
    image3.jpg
    image4.jpg

src_labels/
  dir1/
    image1.txt
    image2.txt
  dir2/
    image3.txt
    image4.txt

На выходе в папке joined нужно будет создать соответсвующие папки dir1, dir2 итд. На примере dir1 из папок src_imgs/dir1/ и src_labels/dir1/  нужно будет скопировать labels, images и положить в соотвествующую папку joined => dir1/labels и dir1/images. Также в корень каждой папки распределения dir1, dir2  положить файлик classes.txt из src_classes. Параметры должны хранится в yaml config

  dir1/
    labels/
        image1.txt
        image2.txt
    images/
        image1.jpg
        image2.jpg