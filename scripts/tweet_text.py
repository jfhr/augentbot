#! python3

import re
from math import sqrt
from typing import Union, Optional

import language_check
import tweepy

IGNORED_USERS = []
MY_NAME = 'augentbot'
lt = language_check.LanguageTool('en-US')


def grammar_check(text: str) -> str:
    return language_check.correct(text, lt.check(text))


def get_weight(tweet: tweepy.models.Status) -> int:
    precise_weight = (tweet.retweet_count*5 + tweet.favorite_count)/sqrt(tweet.author.followers_count)
    limited_weight = min(precise_weight, 25)
    # limit the weight of a single tweet to 25 \
    # to avoid being 'overrun' by one viral tweet

    return int(limited_weight)


def get_viable_text(tweet: tweepy.models.Status) -> Optional[str]:
    if tweet.author.screen_name in IGNORED_USERS:
        return None
    
    string = get_plain_text(tweet.text)

    if re.search('[a-zA-Z]', string) is None:
        return None
    
    return string


def get_plain_text(raw_tweet_text: str) -> str:
    raw_tweet_text = re.sub(r'https://t.co/\S+', '', raw_tweet_text)
    raw_tweet_text = re.sub(r'http://t.co/\S+', '', raw_tweet_text)
    # remove URLs. Since twitter uses an URL shortener, all URLs look like: "https://t.co/Amn4oTgxkD"
    # except URLs from tweets longer ago, these might still look like "http://t.co\Amn4oTgxkD"

    raw_tweet_text = re.sub(r'.?@\w+[: ]', '', raw_tweet_text)
    # remove mentions. Mentions look like "@_jfde" or "@_jfde:"

    raw_tweet_text = re.sub(r'^RT @\w+: ', '', raw_tweet_text)
    # remove retweet identifiers. Retweets in plain text look like: "RT @_jfde: Original tweet text"

    # raw_tweet_text = re.sub(r'#\w+', '', raw_tweet_text)
    # # remove hashtags. Example: "I really like #python!" where "#python" is changed to "python"
    #  ^ experimentally disabled removing hashtags.

    raw_tweet_text = re.sub(r'''[^a-zA-Z0-9_@'\"\-<>?!/\\#., ():\n]''', ' ', raw_tweet_text)
    # remove special characters and emojis.

    raw_tweet_text = re.sub(r'[\n ]+', ' ', raw_tweet_text)
    # remove newlines and multiple whitespaces

    raw_tweet_text = raw_tweet_text.strip()  # remove whitespaces at the beginning or end of a tweet
    raw_tweet_text = grammar_check(raw_tweet_text)  # improve the grammar of these lazy twitter users
    
    return raw_tweet_text


def make_tweet_text(raw_tweet_text: str) -> Union[str, bool]:
    tweet = grammar_check(get_plain_text(raw_tweet_text))
    if not tweet[-1] in {'.', '!', '?', ','}:
        tweet += '.'
    if 0 < len(tweet) <= 140:
        return tweet
    else:
        return False


if __name__ == '__main__':
    # run tests

    print(get_plain_text(r"""@123 https://t.co/f3g foo @_12jfde   bar"""))
