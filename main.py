# coding=utf-8
from sqlalchemy.orm import Session, sessionmaker

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset
from src.dbops import dbOps


def main(full=False):
    paths = return_files_paths()
    print(paths, len(paths))
    # check the full flag
    if full:
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
    from src.dbops import ENGINE
    with ENGINE.connect() as conn:
        while True:
            try:
                dbOps.bulk_dump(next(luke))
            except StopIteration:
                return True


if __name__ == '__main__':
    # set full=True if you want to dump all the downloaded files
    main(full=False)
