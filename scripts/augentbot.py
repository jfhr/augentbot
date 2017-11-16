#! python3

import _io
import os
import platform
from typing import Optional, Iterable, Union

import tweepy

import timestamps
import tweet_text
from pymarkovchain_dynamic import MarkovChain, DynamicMarkovChain

TWITTER_CONSUMER_KEY = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials-beta',
                                         'twitter_consumer_key')).read()
TWITTER_CONSUMER_SECRET = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials-beta',
                                            'twitter_consumer_secret')).read()
TWITTER_ACCESS_TOKEN = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials-beta',
                                         'twitter_access_token')).read()
TWITTER_ACCESS_TOKEN_SECRET = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials-beta',
                                                'twitter_access_token_secret')).read()

HOST_NAME = '_jfde'

DATA = os.path.join(os.path.expanduser('~'), 'augentbot', 'data')

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


def confirm(prompt: str = 'Confirm this action?') -> bool:
    prompt = prompt.strip()
    if not prompt.endswith('?'):
        prompt += '?'
    prompt += ' (y/n): '
    return input(prompt).lower().strip() == 'y'


def notify_me(text: str) -> None:
    """
    send a message to the user specified as HOST_NAME. Messages longer than 10000
    characters will be split in sub-messages due to twitter limits
    """
    for subtext in [text[i:i+10000] for i in range(0, len(text), 10000)]:
        try:
            api.send_direct_message(screen_name=HOST_NAME, text=subtext)
        except tweepy.TweepError as e:
            log_info("{0} when trying to send the following dm:\n    '{1}'".format(e, text))


def log_info(entry: str,
             notify: bool = False,
             file: Optional[_io.TextIOWrapper] = None,
             close_file: bool = True) -> None:
    """
    Attaches a timestamp with the current time to the entry,
    prints the entry and saves it in the log.txt file of the data directory.
    It notify is true, the entry with the add_timestamp will be sent to the
    user specified as HOST_NAME via twitter dm. This requires that the user
    has allowed receiving dms from this account
    """
    if file is None:
        file = open(os.path.join(DATA, "log.txt"), 'a', encoding='utf_16')
    
    file.write(timestamps.add_timestamp(entry) + '\n')
    print(entry)
    if notify:
        notify_me(entry)
    
    if close_file:
        file.close()


def followback() -> None:
    followers = [follower.screen_name for follower in tweepy.Cursor(api.followers).items()]
    # follow back
    followings = [following.screen_name for following in tweepy.Cursor(api.friends).items()]
    for follower in followers:
        if follower not in followings + tweet_text.IGNORED_USERS:
            try:
                api.create_friendship(follower)
                log_info('followed @{0}'.format(follower))
            except tweepy.RateLimitError:
                log_info('Rate limit exceeded.', True)
                break
            except tweepy.TweepError:
                log_info("Couldn't follow @{0}".format(follower))

    # unfollow back
    for following in followings:
        if following not in followers + tweet_text.IGNORED_USERS:
            try:
                api.destroy_friendship(following)
                log_info('unfollowed @{0}'.format(following))
            except tweepy.RateLimitError:
                log_info('Rate limit exceeded.', True)
                break
            except tweepy.TweepError:
                log_info("Couldn't follow @{0}".format(following))


def process_new_tweets() -> None:
    """
    Gets new tweets from the augentbot home timeline, checks every tweet for viability, and adds that tweet to
    the data log. If a tweet has a high weight (many likes and retweets compared to the author's follower count),
    it is being added more often.
    If a tweet older than 7 days is encountered, the method is being returned.
    """
    data_file = open(os.path.join(DATA, 'data.txt'), 'a', encoding='utf_16')
    log_file = open(os.path.join(DATA, 'log.txt'), 'a', encoding='utf_16')
    # don't open and close files for every data/logging entry

    def process_tweet(tweet):
        tweet_value = tweet_text.get_viable_text(tweet)
        if tweet_value:
            log_info("Processing tweet {0}: '{1}' ... viable".format(tweet.author.screen_name, tweet_value),
                     file=log_file, close_file=False)
            for i in range(tweet_text.get_weight(tweet)):
                data_file.write(tweet_value)
        else:
            log_info("Processing tweet {0}: '{1}' ... not viable"
                     .format(tweet.author.screen_name, tweet.text), file=log_file, close_file=False)

    for t in tweepy.Cursor(api.home_timeline, count=240).items():
            process_tweet(t)
    data_file.close()
    log_file.close()
    return


def generate_tweets(count: int = 1, mc: Union[None, MarkovChain, DynamicMarkovChain] = None) -> Iterable[str]:
    if mc is None:
        mc = MarkovChain()

        # using a corpus of predefined data
        with open(os.path.join(DATA, "corpus.txt"), encoding='utf_16') as file:
            corpus_data = file.read()

        # adding the collected data from other twitter users
        with open(os.path.join(DATA, "data.txt"), encoding='utf_16') as file:
            collected_data = file.read()

        mc.generateDatabase(corpus_data+collected_data, n=4)

        del corpus_data
        del collected_data

    tweets = []
    for i in range(count):
        while True:
            tweet = tweet_text.make_tweet_text(mc.generateString())
            if tweet:
                log_info("Added tweet '{}'".format(tweet))
                tweets.append(tweet)
                break

    return tweets


"""
Information on buffer:
In The augentbot data directory lives a file buffer.txt, which contains pre-produced tweets. In case the full augentbot
code throws an exception, a tweet from that file is being tweeted to ensure the bot still keeps tweeting. When producing
a new tweet, one can choose to simultaneously add any number of tweets, produced from the same database, to the 
buffer.txt file, so it always contains a solid amount of tweets.

Example usage:
import augentbot
try:
    augentbot.run(create_buffers=1)
except Exception as e:
    augenbot.tweet_from_buffer()
"""


def tweet_new(create_buffers: int = 0) -> None:
    tweets = list()
    for t in generate_tweets(count=1+create_buffers):
        t_text = tweet_text.make_tweet_text(t)
        if t_text:
            tweets.append(t_text)
            # create a tweet and, if specified in function call, create additional tweets for the tweet buffer

    api.update_status(tweets[0])
    
    if create_buffers:
        with open(os.path.join(DATA, 'buffer.txt'), 'a', encoding='utf_16') as file:
            file.write('\n' + '\n'.join(tweets[1:]))


def tweet_from_buffer() -> None:
    # DynamicMarkovChain is not finished work yet. For now, there is no other way
    # than tweeting from the pre-produced buffer
    with open(os.path.join(DATA, 'buffer.txt'), encoding='utf_16') as file:
        buffer = file.readlines()

    api.update_status(buffer.pop())

    with open(os.path.join(DATA, 'buffer.txt'), 'w', encoding='utf_16') as file:
        file.write(''.join(buffer)[:-1])  # remove newline at end of file


def run(create_buffers: int = 0) -> None:
    try:
        followback()
        process_new_tweets()
        tweet_new(create_buffers)
    except Exception as e:
        log_info(str(e), notify=True)
        try:
            tweet_from_buffer()
        except Exception as e:
            log_info('{} in buffer'.format(str(e)), notify=True)

    
if __name__ == '__main__':
    if platform.system() == 'Windows':
        os.system('chcp 65001')  # fixes encoding errors on windows

    generate_tweets()
