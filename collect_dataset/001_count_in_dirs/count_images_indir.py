import os
import pandas as pd

import argparse
import textwrap

# python3 count_images_indir.py -s /home/arch/Documents/project/angel/image_classification/dataset/prepare_data -c collector_black_case collector_case collector_no_case person undefined


def get_empty_dict(list_classes):
   # l=[  'collector_black_case',
   #       'collector_case',
   #       'collector_no_case',
   #       'person',
   #       'undefined']
   d={}
   for i in list_classes:
      d[i]=0
   return d

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
    parser.add_argument('-s', '--src', type=str, required=True)
    parser.add_argument('-c', '--classes', nargs='+', help='<Required> Set flag', required=True)
    parser.add_argument('-o', '--out', type=str,  default='out.csv', required=False)

    args = parser.parse_args()

    src=args.src
    print(f"src {src}")
    list_classes = sorted(args.classes)
    print(f"list_classes {list_classes}")
    out =args.out
    print(f"out {out}")



    # Main program  
    df = pd.DataFrame(columns=[  'name_set' ] + list_classes )


    for name_set in os.listdir(src):
       pth_nameset=os.path.join(src, name_set)
       if not os.path.isdir(pth_nameset):
          continue
       list_inside_dir = os.listdir(pth_nameset)
       if "sorted" in list_inside_dir:
          slovr2pandas={'name_set':name_set}
          for name_class in get_empty_dict(list_classes):
                end_pth=os.path.join(pth_nameset, "sorted", name_class)
                amount_img=len(os.listdir(end_pth))
                slovr2pandas[name_class]=amount_img
          slovr2pandas = pd.DataFrame([slovr2pandas])
          df = pd.concat([df, slovr2pandas], ignore_index=True)
    df = df.sort_values('name_set')
    print(df)
    
    df.to_csv(out, sep='\t', encoding='utf-8')





