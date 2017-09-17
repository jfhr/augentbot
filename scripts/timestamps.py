#! python3

import datetime


def add_timestamp(entry):
    timestamp = str(tuple(datetime.datetime.utcnow().timetuple())[:6])
    timestamp = '{0}{1} '.format(' ' * (25 - len(timestamp)), timestamp)
    return timestamp + entry


def remove_timestamp(entry):
    return entry[27:]


def write_with_timestamps(file, entries):
    for e in entries:
        file.write(add_timestamp(e))


def read_wo_timestamps(entries):
    return [remove_timestamp(e) for e in entries]
