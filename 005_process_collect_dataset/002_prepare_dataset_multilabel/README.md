
## 001 Изначально должна быть подготовленная таблица

| Name                           | collector_black_case | collector_case | collector_no_case | person | undefined |   |   |   |   |
|--------------------------------|----------------------|----------------|-------------------|--------|-----------|---|---|---|---|
| 001_inside_car_incass_DONE     | 3                    | 9              | 866               | 425    | 165       |   |   |   |   |
| 003_ift_stand_inside_car_DONE  | 3                    | 7              | 543               | 1024   | 1303      |   |   |   |   |
| 004_ift_stand_outside_car_DONE | 97                   | 44             | 458               | 791    | 958       |   |   |   |   |
| 006_1_ift_outside              | 118                  | 63             | 891               | 1756   | 1086      |   |   |   |   |
| 006_2_ift_inside               | 0                    | 0              | 436               | 149    | 0         |   |   |   |   |
|                                |                      |                |                   |        |           |   |   |   |   |

## Согласно этой csv таблице мы предарительно собираем датасет в отдельную папку  
То-есть рандомно отбираются то количество сепвлов указанных в данной ячейке csv

```
python3 001_recollect_dataset.py --src-csv "/home/arch/Документы/project/angel/incass_classification/dataset/trains/003_train/train_set.csv" \
--src-data /home/arch/Документы/project/angel/incass_classification/dataset/prepared_data_001/ \
--dst-data /home/arch/Документы/project/angel/incass_classification/dataset/trains/003_train/tmp_collect/
```


## 2 Ре-лейблинг с классификации to multilabel

'''
python3 002_create_YAML_file.py --src-dir ./incass_classification/dataset/trains/003_train/003_data_train_incass_multilabel/train/ \
--pth-in-YAML ./example.yaml \
--pth-out-YAML ./process_collect_dataset/002_prepare_dataset_multilabel/111
'''

YAML
```
collector_black_case:
  class_case: 0
  class_person: 1
collector_case:
  class_case: 1
  class_person: 1
collector_no_case:
  class_case: 2
  class_person: 1
person:
  class_case: 2
  class_person: 0
undefined:
  class_case: 2
  class_person: 0
```

аналогично

json
```
{"collector_black_case":{"class_case":0,
                                  "class_person":1},
          "collector_case":      {"class_case":1,
                                  "class_person":1},
          "collector_no_case":   {"class_case":2,
                                  "class_person":1},
          "person":              {"class_case":2,
                                  "class_person":0},
          "undefined":           {"class_case":2,
                                  "class_person":0},}
```

### OUTPUT
```
003_ift_stand_inside_car_DONE/person/0.975_c3f9f3de-9e55-11ed-bfdf-48b02d3d8a0e_hccjwqgd_0.png:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.982_b8da42f0-c77d-11ed-8656-48b02d3d8b52_1gz52wj1_1.png:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.98_74c78b1c-c274-11ed-a418-48b02d3d8a04_jknt9g80_0.png:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.998_0269e620-7088-11ed-9e42-48b02d3d8b52_khvx8miv_1.jpg:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.995_b81e209e-666a-11ed-9078-48b02d3d8a0e_2ye7cuug_0.jpg:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.992_f09b7a56-77e6-11ed-b02c-48b02d3d8a0e_2crd7u4z_1.jpg:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.953_1720ae18-ca57-11ed-bc40-48b02d3d8b52_t72gkd1y_2.png:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.984_ec04c7ac-7ae5-11ed-a888-48b02d3d8a0e_v1vj375l_1.jpg:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.919_2ee49750-7af0-11ed-ad97-48b02d3d8b52_u2q1g88f_3.jpg:
  class_case: 2
  class_person: 0
003_ift_stand_inside_car_DONE/person/0.746_b0225ab8-c98e-11ed-ace5-48b02d3d8b52_58i0_jmt_2.png:
  class_case: 2
  class_person: 0
```