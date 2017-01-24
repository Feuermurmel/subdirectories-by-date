import datetime
import os
import re
import sys
from subprocess import Popen, PIPE

from lib.util import log, walk_visible_files, move_to


class CommandError(Exception):
    pass


def exiftool(file_path):
    exiftool_name = os.environ.get('EXIFTOOL', 'exiftool')
    command = [exiftool_name, '-s', '-t', file_path]
    process = Popen(command, stdout=PIPE)
    output, _ = process.communicate()

    if process.returncode:
        raise CommandError(
            'Error: Command exited with status {}: {}'.format(
                process.returncode, ' '.join(command)))

    return dict(i.split('\t', 1) for i in output.decode().splitlines())


def get_capture_date(file_path):
    try:
        metadata = exiftool(file_path)
    except CommandError as e:
        log('{}', e)

        return None

    capture_date_attributes = \
        'DateTimeOriginal MediaCreateDate CreateDate CreationDate ' \
        'DateCreated'.split()

    for i in capture_date_attributes:
        value = metadata.get(i)

        if value is not None:
            break
    else:
        return None

    pattern = '(?P<year>[0-9]{4})[:-]' \
              '(?P<month>[0-9]{2})[:-]' \
              '(?P<day>[0-9]{2}) ' \
              '(?P<hour>[0-9]{2}):' \
              '(?P<minute>[0-9]{2}):' \
              '(?P<second>[0-9]{2})(\.[0-9]+)?([+-[0-9]{2}:[0-9]{2})?'

    match = re.match(pattern, value)

    assert match, 'Could not parse date: {}'.format(value)

    return datetime.datetime(
        *(
            int(match.group(i))
            for i in 'year month day hour minute second'.split()))


def main(source_dir, target_dir):
    for i in walk_visible_files(source_dir):
        base_name, ext = os.path.splitext(os.path.basename(i))
        capture_date = get_capture_date(i)

        if capture_date is not None:
            base_name = capture_date.strftime('%Y-%m-%d %H.%M.%S')

        target_path = os.path.join(target_dir, base_name + ext.lower())
        move_to(i, target_path)


try:
    main(*sys.argv[1:])
except KeyboardInterrupt:
    log('Operation interrupted.')
