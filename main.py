# coding=utf-8
import sys

__author__ = 'Lorenzo'

from files.loadfiles import return_dataset, return_files_paths
from src.formatdata import create_generator_from_dataset
from src.storedata import namedtuple_values_to_sql, go_execute

def main():
    paths = return_files_paths()
    print(paths, len(paths))
    # try the first file
    dataset = return_dataset(paths[1])
    luke = create_generator_from_dataset(dataset)
    print(luke, )

    # consume the generator
    for point in luke:
        try:
            go_execute(namedtuple_values_to_sql(point))
            next(luke)
        except StopIteration:
            break
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            continue


if __name__ == '__main__':
    main()
