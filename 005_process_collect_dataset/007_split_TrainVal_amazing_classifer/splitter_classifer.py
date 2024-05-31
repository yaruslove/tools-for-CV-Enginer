






import argparse
import textwrap








if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Classifier training program',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                         Data dir example:
                                            data/ <-- path src to this dir [--data] argument
                                            ├──001_class/
                                            │  └─sorted/
                                            │     ├──<class_1>
                                            │     ├──<class_2>
                                            │     └──<class_N>
                                            │
                                            │
                                            │
                                            ├──002_class/
                                            │  └─sorted/
                                            │     ├──<class_1>
                                            │     ├──<class_2>
                                            │     └──<class_N>
                                            │
                                            ........
                                            ........
                                            │
                                            └──XXX_class/
                                               └─sorted/
                                                  ├──<class_1>
                                                  ├──<class_2>
                                                  └──<class_N>

                                         '''))
    # Get aruments  

    parser.add_argument('-s', '--src', type=str, required=True)
    parser.add_argument('-d', '--dst', type=str, required=False)
    parser.add_argument('--percentage_train', type=int, required=False)

    args = parser.parse_args()

    src =args.src
    dst =args.dst
    percentage_train=args.percentage_train
    
    