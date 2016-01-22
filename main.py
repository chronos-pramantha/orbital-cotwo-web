# coding=utf-8
"""
This script will dump all the files (or a test sample) from the files/nc4/
directory
"""

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset
from src.xco2ops import xco2Ops


def main(full=False):
    paths = return_files_paths()
    print(paths, len(paths))
    # check the full flag
    if not full:
        # try the first thousand rows of the first file
        dataset = [return_dataset(paths[1])]
        luke = (create_generator_from_dataset(d, 1000) for d in dataset)
    else:
        # dump all the files
        dataset = []
        dataset += [return_dataset(p) for p in paths]
        luke = (create_generator_from_dataset(d) for d in dataset)
    #print(luke, )

    # consume the generator of generators
    # change database name below ('test' or 'gis') to decide which one to use
    print('DUMPING...')
    i = 0

    while True:
        try:
            xco2Ops.bulk_dump(next(luke))
            i += 1
        except StopIteration:
            print('>>> XCO2 Dump finished <<<')
        if i % 1000 == 0:
            print(i)


if __name__ == '__main__':
    # set full=True if you want to dump all the downloaded files
    main(full=False)
