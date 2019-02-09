import datetime
import os
import sys

from lib.util import log, move_to, remove_dir, walk_visible_files


date_format = '%G/%G-W%V/%G-W%V-%u'


def main(dir):
    def is_empty(dir):
        return os.path.exists(dir) \
               and all(i.startswith('.') for i in os.listdir(dir))

    def dir_for_date(date):
        return os.path.join(dir, date.strftime(date_format))

    check_empty_dirs = []

    for i in walk_visible_files(dir):
        file_dir, file_name = os.path.split(i)
        name_part, _ = os.path.splitext(file_name)

        try:
            date = datetime.datetime.strptime(
                name_part[:19],
                '%Y-%m-%d %H.%M.%S')

            target_dir = dir_for_date(date)
        except ValueError:
            target_dir = os.path.join(dir, 'unknown')

        move_to(i, os.path.join(target_dir, file_name))
        check_empty_dirs.append(file_dir)

    while check_empty_dirs:
        empty_dirs = check_empty_dirs
        check_empty_dirs = []

        for i in empty_dirs:
            if is_empty(i):
                remove_dir(i)
                check_empty_dirs.append(os.path.dirname(i))


try:
    main(*sys.argv[1:])
except KeyboardInterrupt:
    log('Operation interrupted.')
