Есть команда конвертатора.
```bash
label-studio-converter import yolo -i /yolo/datasets/one -o output.json --image-root-url "/data/local-files/?d=one/images"
```

Тебе нужно написать python программу которая в цикле берет переменную inside_name название переменное название одной из внутреней папки src_yolo, далее создает полный путь к папкам внутри src_yolo full_path_inside_name. 
full_path_inside_name=os.path.join(src_yolo,inside_name) 
В цикле пробегает имена директорий внутри src_yolo и подставляет полный full_path_inside_name путь на место пути в bash команде "/yolo/datasets/one". 
dst_LabelStudio - путь где будут создаваться папки, внутри которых будет создаваться json.
Далее создает папку по названию имени директории из src_yolo, название создаваемых папок в цикле и хранится в переменной inside_name. Путь выхода: dst_path=os.path.join(dst_LabelStudio,inside_name). далее будет созданна переменная variable_bash_dst_json=os.path.join(dst_LabelStudio,inside_name, f"{inside_name}.json") 
В этих циклах или цикле даннвые перменные будут подставлятся в bash команду:
-o output.json = variable_bash_dst_json
-i /yolo/datasets/one будет подставлятся в цикле full_path_inside_name
ольше ничего в команде label-studio-converter имзенятся не будет. Команда bash будет вызыватся каждый раз в цикле
Python программе должен быть config с переменными
src_yolo
dst_LabelStudio