# coding=utf-8
from sqlalchemy.orm import Session, sessionmaker

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset, bulk_dump
from src.xco2 import start_postgre_engine


def main():
    paths = return_files_paths()
    print(paths, len(paths))
    # try the first file
    dataset = return_dataset(paths[1])
    luke = create_generator_from_dataset(dataset)
    print(luke, )

    # consume the generator
    engine = start_postgre_engine('gis', True)
    with engine.connect() as conn:
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        bulk_dump(session, luke)


if __name__ == '__main__':
    main()
