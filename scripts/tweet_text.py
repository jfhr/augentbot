#! python3

import re
from math import sqrt

import language_check
import tweepy

IGNORED_USERS = ['_jfde', 'augentbot', 'augentbot_beta']
MY_NAME = 'augentbot'
lt = language_check.LanguageTool('en-US')


def grammar_check(text: str) -> str:
    return language_check.correct(text, lt.check(text))


def get_weight(tweet: tweepy.Status) -> int:
    r = tweet.retweet_count
    f = tweet.favorite_count
    p = tweet.author.followers_count

    return (r*5 + f)/sqrt(p)


def viable(tweet: tweepy.Status) -> bool:
    # Finds out if a tweet is allowed to be added to the database.
    # Tweets are not allowed if they
    #  - contain no text (e.g. pure picture tweets, or tweets that contain only URLs)
    #  - come from an ignored user
    o_string = tweet.text
    string = get_plain(o_string)

    return (string != '') and (tweet.author.screen_name not in IGNORED_USERS)


def get_plain(string: str) -> str:
    string = re.sub(r'https://t.co/\S+', '', string)
    # remove URLs. Since twitter uses an URL shortener, all URLs look like: "https://t.co/Amn4oTgxkD"

    string = re.sub(r'.?@\w+[: ]', '', string)
    # remove mentions. Mentions look like "@_jfde" or "@_jfde:"

    string = re.sub(r'[\n ]+', ' ', string)
    # remove newlines and multiple whitespaces

    string = re.sub(r'^RT', ' ', string)
    # remove retweet identifiers. Retweets in plain text look like: "RT @_jfde: Original tweet text"

    # string = re.sub(r'#\w+', '', string)
    # # remove hashtags. Example: "I really like #python!" where "#python" is changed to "python"
    #  ^ experimentally disabled removing hashtags.

    string = re.sub(r'''[^a-zA-Z0-9_@'\"\-<>?!/\\#., ():\n]''', ' ', string)
    # remove special characters and emojis.

    string = string.strip()  # remove whitespaces at the beginning or end of a tweet
    string = grammar_check(string)  # improve the grammar of these lazy twitter users
    return string


def make_tweet_text(raw_tweet: str) -> str:
    tweet = grammar_check(get_plain(raw_tweet))
    if not tweet[-1] in {'.', '!', '?'}:
        if tweet.endswith(','):
            tweet = tweet[:-1] + ','
        else:
            tweet += '.'
    if len(tweet) <= 140:
        return tweet
    else:
        return False


if __name__ == '__main__':
    # run tests

    print(get_plain(r"""@123 https://t.co/f3g foo @_12jfde   bar"""))
