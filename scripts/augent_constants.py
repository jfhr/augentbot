#! python3.6

import _io
from os.path import expanduser as usr
from typing import List

import tweepy

with open(usr('~/augentbot/credentials/twitter_consumer_key')) as file:
    TWITTER_CONSUMER_KEY: str = file.read()
with open(usr('~/augentbot/credentials/twitter_consumer_secret')) as file:
    TWITTER_CONSUMER_SECRET: str = file.read()
with open(usr('~/augentbot/credentials/twitter_access_token')) as file:
    TWITTER_ACCESS_TOKEN: str = file.read()
with open(usr('~/augentbot/credentials/twitter_access_token_secret')) as file:
    TWITTER_ACCESS_SECRET: str = file.read()

HOST_NAME: str = '_jfde'

auth: tweepy.OAuthHandler = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

api: tweepy.API = tweepy.API(auth)

with open(usr('~/augentbot/data/ignored.txt')) as file:
    IGNORED_USERS: List[str] = file.readlines()

log_file: _io.TextIOWrapper = open(usr('~/augentbot/data/log.txt'), 'a', encoding='utf_16', buffering=1)
data_file: _io.TextIOWrapper = open(usr('~/augentbot/data/data.txt'), 'a', encoding='utf-16', buffering=1)
buffer_file: _io.TextIOWrapper = open(usr('~/augentbot/data/buffer.txt'), 'a', encoding='utf-16', buffering=1)

coll_data: str = ''
corpus_data: str = ''
buffer_data: List[str] = ['', ]


def read_coll():
    global coll_data
    with open(usr('~/augentbot/data/data.txt'), encoding='utf-16') as file:
        coll_data = file.read()


def read_corpus():
    global corpus_data
    with open(usr('~/augentbot/data/log.txt'), 'r', encoding='utf_16') as file:
        corpus_data = file.read()


def read_buffer():
    global buffer_data
    with open(usr('~/augentbot/data/buffer.txt'), encoding='utf-16') as file:
        buffer_data = file.readlines()
