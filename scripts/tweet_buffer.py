#! python3.6
from typing import List

from .config import *


__all__ = ['get_buffered_tweet', 'append_tweets_to_buffer', 'BufferEmptyException']


class BufferEmptyException(Exception):
    pass


file = open(BUFFER_FILE, 'r+', errors='ignore')
file.seek(0)


def get_buffered_tweet() -> str:
    tweet = file.readline()
    if tweet == '':
        raise BufferEmptyException
    return tweet


def append_tweets_to_buffer(*tweets: str) -> None:
    file.write('\n'.join(tweets))
    file.write('\n')
    file.seek(0)
