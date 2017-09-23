import language_check
import re

# BLACKLISTED_WORDS = ['retweet', 'rt ', 'like', 'follo', 'ctl', 'cross the line', 'ifb']
# Blacklisted words - feature has been deactivated
ALLOWED_CHARS = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_@'"-<>?!/\\#., ()\n"""
MY_NAME = 'augentbot'
lt = language_check.LanguageTool('en-US')


def grammar_check(text):
    return language_check.correct(text, lt.check(text))


def get_weight(tweet):
    r = tweet.retweet_count
    f = tweet.favorite_count
    p = tweet.author.followers_count

    if tweet.author.screen_name != MY_NAME:
        return round(((tweet.retweet_count*3 + tweet.favorite_count)/tweet.author.followers_count) * 50) + 1
    else:
        return (r*5 + f)/p
        return ((tweet.retweet_count*5 + tweet.favorite_count)*10/tweet.author.followers_count) ^ 3 * 10


def viable(tweet):
    # Finds out if a tweet is allowed to be added to the database.
    # Tweets are not allowed if they
    #  - contain no text (e.g. pure picture tweets, or tweets that contain only URLs)
    #  - 
    o_string = tweet.text
    string = get_plain(o_string)

    return (string != '')
       and tweet.author.screen_name not in IGNORED_USERS

def augent_decode(string):
    dec_string = ''.join([c if c in ALLOWED_CHARS else ' ' for c in string])
    return dec_string


def get_plain(string):
    string = re.sub(r'https://t.co/\S+', '', string)
    string = re.sub(r'.?@\w+[: ]', '', string)
    string = re.sub(r'[\n ]+', ' ', string)
    string = re.sub(r'^RT', ' ', string)
    string = re.sub(r'#\w+', '', string)
    string = re.sub(r'''[^a-zA-Z0-9_@'\"\-<>?!\/\\#., ():\n]''', ' ', string)
    string = augent_decode(string)
    string = string.strip()
    return string


def make_tweet(raw_tweet):
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
