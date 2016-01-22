# coding=utf-8
"""
This script will dump all the files (or a test sample) from the files/nc4/
directory
"""

__author__ = 'Lorenzo'

from random import randint
from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset


def main(full=False):
    paths = return_files_paths()
    print(paths, len(paths))
    # check the full flag
    if not full:
        l = randint(0, len(paths) - 1)
        # try the first thousand rows of one random file
        dataset = [return_dataset(paths[l])]
        luke = (create_generator_from_dataset(d, 1000) for d in dataset)
    else:
        # dump all the files
        dataset = []
        dataset += [return_dataset(p) for p in paths]
        luke = (create_generator_from_dataset(d) for d in dataset)
    #print(luke, )

    # Luke is a >> generator of generators <<
    # Feel the Force
    print('DUMPING...')
    from src.formatdata import bulk_dump
    i = 0
    while True:
        try:
            _, n = bulk_dump(next(luke))
            i += n
        except StopIteration:
            print('>>> {} Xco2 data dumped <<<'.format(i))
            break
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    # set full=True if you want to dump all the downloaded files
    main(full=True)
