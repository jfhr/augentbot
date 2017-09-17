import language_check
import re

BLACKLISTED_WORDS = ['retweet', 'rt ', 'like', 'follo', 'ctl', 'cross the line', 'ifb']
ALLOWED_CHARS = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_@'"-<>?!/\\#., ()\n"""
lt = language_check.LanguageTool('en-US')


def grammar_check(text):
    return language_check.correct(text, lt.check(text))


def viable(tweet):
    o_string = tweet.text
    string = get_plain(o_string)
    return (not any(w in string.lower() for w in BLACKLISTED_WORDS)) \
        and (string != '') \
        and all(c in ALLOWED_CHARS for c in o_string)


def augent_decode(string):
    string = re.sub(r'''[^a-zA-Z0-9_@'\"\-<>?!\/\\#., ():\n]''', ' ', string)
    return string


def get_plain(string):
    string = re.sub(r'https://t.co/\S+', '', string)
    string = re.sub(r'.?@\w+[: ]', '', string)
    string = re.sub(r'[\n ]+', ' ', string)
    string = re.sub(r'^RT', ' ', string)
    string = augent_decode(string)
    string = string.strip()
    return string


def make_tweet(raw_tweet):
    tweet = grammar_check(get_plain(raw_tweet))
    if not tweet[-1] in {'.', '!', '?'}:
        tweet += '.'
    if len(tweet) <= 140:
        return tweet
    else:
        return False


if __name__ == '__main__':
    # run tests

    print(get_plain(r"""@123 https://t.co/f3g foo @_12jfde   bar"""))
