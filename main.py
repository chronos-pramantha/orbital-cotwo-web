# coding=utf-8
from sqlalchemy.orm import Session, sessionmaker

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset
from src.dbops import start_postgre_engine, dbOps

# TEST variable set in config/config.py
# if true, only the first thousand rows of the first file are dumped
# if false, all the files in files/nc4 are dumped (WARN: can take more than 30 minutes)
from config.config import TEST


def main(test=TEST):
    paths = return_files_paths()
    print(paths, len(paths))
    if test:
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
    _, engine = start_postgre_engine('test', True)
    with engine.connect() as conn:
        while True:
            try:
                dbOps.bulk_dump(next(luke))
            except StopIteration:
                return True


if __name__ == '__main__':
    main()
