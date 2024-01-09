import os
import glob
import textwrap
import argparse


class StoreDictKeyPair(argparse.Action):
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values.split(","):
             k,v = kv.split("=")
             k=int(k)
             my_dict[k] = int(v)
         setattr(namespace, self.dest, my_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Cut bbox yolo',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''Cut bbox yolo from txt labels'''))

    parser.add_argument('-l', '--labels_pth', type=str, required=True)
    parser.add_argument('-z','--zamena', action=StoreDictKeyPair, metavar='KEY1=VAL1,KEY2=VAL2...') #, dest='my_dict'

    args = parser.parse_args()
    print(args)

    labels_pth=args.labels_pth
    zamena=args.zamena

    print("labels_pth",labels_pth)
    print("zamena",zamena)


    for lab in glob.glob(f'{labels_pth}/*.txt'):
        if os.stat(lab).st_size == 0:
            continue
        f = open(lab,'r')
        context = f.read()
        f.close()
        context=context.strip().split("\n")
        write_context=""
        for row in context:
            nach_class=int(row[:row.find(" ")])
            if nach_class in list(zamena.keys()):
                for key_zam in zamena:
                    if nach_class==key_zam:
                        row=str(zamena[key_zam])+row[row.find(" "):]
                        break
                write_context=(write_context+"\n"+row).strip()
            else:
                write_context=(write_context+"\n"+row).strip()
        f = open(lab, 'r+')
        f.truncate(0)
        f.write(write_context)
        f.close()