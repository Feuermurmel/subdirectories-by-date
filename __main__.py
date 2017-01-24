import datetime
import os
import re
import shutil
import sys
from itertools import count


date_format = '%G/%G-W%V/%G-W%V-%u'


def log(message, *args):
    print(message.format(*args), file=sys.stderr)


def read_file(path):
    with open(path, 'rb') as file:
        return file.read()


def make_dirs(path):
    if not os.path.exists(path):
        log('Creating {}', path)
        os.makedirs(path)


def split_numbered_file_name(file_name):
    base_name, suffix = os.path.splitext(file_name)
    match = re.match(
        '(?P<prefix>.+?)( (?P<number>[2-9]|[1-9][0-9]+))?$',
        base_name)

    return match.group('prefix'), suffix


def join_numbered_file_name(prefix, number, suffix):
    if number > 1:
        number_part = ' {}'.format(number)
    else:
        number_part = ''

    return ''.join([prefix, number_part, suffix])


def move_to(source_path, target_dir):
    prefix, suffix = split_numbered_file_name(
        os.path.basename(source_path))

    for i in count(1):
        target_path = os.path.join(
            target_dir,
            join_numbered_file_name(prefix, i, suffix))

        if not os.path.exists(target_path) \
                or read_file(source_path) == read_file(target_path):
            break

    if source_path != target_path:
        make_dirs(target_dir)
        log('Moving {} to {}', source_path, target_path)
        os.rename(source_path, target_path)


def remove_dir(path):
    log('Removing {}', path)
    shutil.rmtree(path)


def main(dir):
    def unsort_images():
        for dirpath, dirnames, filenames in os.walk(dir):
            for entries in dirnames, filenames:
                entries[:] = [i for i in entries if not i.startswith('.')]

            for i in filenames:
                _, ext = os.path.splitext(i)

                if ext in ['.jpg', '.png', '.mov', '.mp4']:
                    yield os.path.join(dirpath, i)

    def is_empty(dir):
        return os.path.exists(dir) \
               and all(i.startswith('.') for i in os.listdir(dir))

    def dir_for_date(date):
        return os.path.join(dir, date.strftime(date_format))

    check_empty_dirs = []

    for i in unsort_images():
        file_dir, file_name = os.path.split(i)
        name_part, _ = os.path.splitext(file_name)

        try:
            date = datetime.datetime.strptime(
                name_part[:19],
                '%Y-%m-%d %H.%M.%S')
        except ValueError:
            log('Could not extract date from file name: {}', file_name)
        else:
            move_to(i, dir_for_date(date))
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
