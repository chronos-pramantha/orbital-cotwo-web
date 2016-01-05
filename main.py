# coding=utf-8
__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset


def main():
    paths = return_files_paths()
    print(paths)
    dataset = return_dataset(paths[0])
    luke = create_generator_from_dataset(dataset)

    for p in luke:
        print(p)
        try:
            next(luke)
        except StopIteration:
            break


if __name__ == '__main__':
    main()
