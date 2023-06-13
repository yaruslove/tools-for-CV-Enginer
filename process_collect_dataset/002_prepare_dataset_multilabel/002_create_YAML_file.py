import yaml
import os
import argparse
import textwrap

def write_yaml_to_file(py_obj,filename):
    yaml.Dumper.ignore_aliases = lambda *args : True
    with open(f'{filename}.yaml', 'w',) as f :
        yaml.dump(py_obj,f,sort_keys=False) 
    print('Written to file successfully !!!')


def create_YAML_labels(dir_src,slovar,pth_out_YAML):
    train_label_dict={}
    for upper_dir in os.listdir(dir_src):
        path_dir_sample=os.path.join(dir_src,upper_dir)
        for class_dir in os.listdir(path_dir_sample):
            current_label=slovar[class_dir]
    
            path_dir_class=os.path.join(path_dir_sample,class_dir)
            for img_pth in os.listdir(path_dir_class):
                key_YAML=os.path.join(upper_dir,class_dir,img_pth)
                train_label_dict[key_YAML]=current_label
    
    # write YAML file
    write_yaml_to_file(train_label_dict,pth_out_YAML)
    print('Process done!!!')
    return  train_label_dict


'''
python3 002_create_YAML_file.py --src-dir "/home/arch/Документы/project/angel/incass_classification/dataset/trains/003_train/003_data_train_incass_multilabel/train/" \
--pth-in-YAML /home/arch/Документы/git/tools-for-CV-Enginer/process_collect_dataset/002_prepare_dataset_multilabel/example.yaml \
--pth-out-YAML /home/arch/Документы/git/tools-for-CV-Enginer/process_collect_dataset/002_prepare_dataset_multilabel/111
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Classifier training program',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
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

                                         '''))
    # Get aruments  
    parser.add_argument('--src-dir', type=str, required=True)
    parser.add_argument('--pth-in-YAML', type=str, required=True, help='path with initiall data with files')
    parser.add_argument('--pth-out-YAML', type=str, required=True, help='path with initiall data with files')

    args = parser.parse_args()

    src_dir=args.src_dir
    pth_in_YAML=args.pth_in_YAML
    pth_out_YAML=args.pth_out_YAML

    # pre load yaml-slovar
    with open(pth_in_YAML, "r") as stream:
        try:
            loaded_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


    label_dict=create_YAML_labels(src_dir, loaded_yaml, pth_out_YAML)
