import os
import re
import shutil
import sys
from itertools import count


def log(message, *args):
    print(message.format(*args), file=sys.stderr)


def move_to(source_path, target_path):
    target_dir = os.path.dirname(target_path)
    prefix, suffix = split_numbered_file_name(
        os.path.basename(target_path))

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


def remove_dir(path):
    log('Removing {}', path)
    shutil.rmtree(path)


def walk_visible_files(dir_path):
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for entries in dirnames, filenames:
            entries[:] = [i for i in entries if not i.startswith('.')]

        for i in filenames:
            yield os.path.join(dirpath, i)
