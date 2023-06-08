## Подсчет картинок по классам

Данный скрипт бежит по папка в директории, там находит папку **sorted** и внутри нее подсчитывает классы
### INPUT
В параметр **--src** указывается путь до директории внутри которого расположенна даная структура файлов

```
        Data dir example:
        data/ <-- path src to this dir [--data] argument
        ├──001_first_image_set/
        │  └─sorted/
        │     ├──<class_1>
        │     ├──<class_2>
        │     └──<class_N>
        │
        │
        │
        ├──002_second_image_set/
        │  └─sorted/
        │     ├──<class_1>
        │     ├──<class_2>
        │     └──<class_N>
        │
        ........
        ........
        │
        └──XXX_N_image_set/
            └─sorted/
                ├──<class_1>
                ├──<class_2>
                └──<class_N>

```

### OUTPUT

file .csv  
| name_set                        | collector_black_case | collector_case | collector_no_case | person | undefined |   |   |   |   |
|---------------------------------|----------------------|----------------|-------------------|--------|-----------|---|---|---|---|
| 001_inside_car_incass_DONE!     | 3                    | 9              | 4333              | 425    | 165       |   |   |   |   |
| 002_out_car_incass_DONE!        | 58                   | 10             | 175               | 1787   | 446       |   |   |   |   |
| 003_ift_stand_inside_car_DONE!  | 3                    | 7              | 10877             | 1708   | 1303      |   |   |   |   |
| 004_ift_stand_outside_car_DONE! | 97                   | 44             | 458               | 1319   | 958       |   |   |   |   |
| 010_Postanovka_Abza             | 1939                 | 1100           | 191               | 3757   | 1970      |   |   |   |   |
|                                 |                      |                |                   |        |           |   |   |   |   |


### Команда запуска:
```
python3 count_images_indir.py -s /home/arch/data \
-c collector_black_case collector_case collector_no_case person undefined \
-o out.csv
```