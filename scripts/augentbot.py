#! python3.6

import datetime
import platform
from typing import List, Union

import augent_constants
import timestamps
import tweet_text
from pymarkovchain_dynamic import MarkovChain, DynamicMarkovChain


def notify_me(text: str) -> None:
    """
    send a message to the user specified as HOST_NAME. Messages longer than 10000
    characters will be split in sub-messages due to twitter limits
    """
    for subtext in [text[i:i+10000] for i in range(0, len(text), 10000)]:
        try:
            augent_constants.api.send_direct_message(screen_name=augent_constants.HOST_NAME, text=subtext)
        except augent_constants.tweepy.TweepError as e:
            log_info("{0} when trying to send the following dm:\n    '{1}'".format(e, text))


def log_info(entry: str, notify: bool = False) -> None:
    """
    Attaches a timestamp with the current time to the entry,
    prints the entry and saves it in the log.txt file of the data directory.
    It notify is true, the entry with the add_timestamp will be sent to the
    user specified as HOST_NAME via twitter dm. This requires that the user
    has allowed receiving dms from this account
    """
    augent_constants.log_file.write(timestamps.add_timestamp(entry) + '\n')
    print(entry)
    if notify:
        notify_me(entry)


def followback() -> None:
    followers = [follower.screen_name for follower in
                 augent_constants.tweepy.Cursor(augent_constants.api.followers).items()]
    # follow back
    followings = [following.screen_name for following in
                  augent_constants.tweepy.Cursor(augent_constants.api.friends).items()]
    for follower in followers:
        if follower not in followings + augent_constants.IGNORED_USERS:
            try:
                augent_constants.api.create_friendship(follower)
                log_info('followed @{0}'.format(follower))
            except augent_constants.tweepy.RateLimitError:
                log_info('Rate limit exceeded.', True)
                break
            except augent_constants.tweepy.TweepError:
                log_info("Couldn't follow @{0}".format(follower))

    # unfollow back
    for following in followings:
        if following not in followers + augent_constants.IGNORED_USERS:
            try:
                augent_constants.api.destroy_friendship(following)
                log_info('unfollowed @{0}'.format(following))
            except augent_constants.tweepy.RateLimitError:
                log_info('Rate limit exceeded.', True)
                break
            except augent_constants.tweepy.TweepError:
                log_info("Couldn't follow @{0}".format(following))


def process_new_tweets() -> None:
    """
    Gets new tweets from the augentbot home timeline, checks every tweet for viability, and adds that tweet to
    the data log. If a tweet has a high weight (many likes and retweets compared to the author's follower count),
    it is being added more often.
    If a tweet older than 7 days is encountered, the method is being returned.
    """
    def process_tweet(tweet):
        tweet_value = tweet_text.get_viable_text(tweet)
        if tweet_value:
            log_info("Processing tweet {0}: '{1}' ... viable".format(tweet.author.screen_name, tweet_value))
            for i in range(tweet_text.get_weight(tweet)):
                augent_constants.data_file.write(tweet_value)
        else:
            log_info("Processing tweet {0}: '{1}' ... not viable".format(tweet.author.screen_name, tweet.text))

    for t in augent_constants.tweepy.Cursor(augent_constants.api.home_timeline, count=168).items():
        if t.created_at < datetime.datetime.now() - datetime.timedelta(days=7):
            return
        process_tweet(t)
    return


def generate_tweets(count: int = 1, mc: Union[None, MarkovChain, DynamicMarkovChain] = None) -> List[str]:
    temporary_markov_chain = False
    if mc is None:
        augent_constants.read_coll()
        augent_constants.read_corpus()
        temporary_markov_chain = True
        mc: MarkovChain = MarkovChain()
        mc.generateDatabase(augent_constants.corpus_data + augent_constants.coll_data, n=4)

    tweets: augent_constants.List[str] = []
    for i in range(count):
        while True:
            tweet = tweet_text.make_tweet_text(mc.generateString())
            if tweet:
                log_info("Added tweet '{}'".format(tweet))
                tweets.append(tweet)
                break

    if temporary_markov_chain:
        del mc

    return tweets


"""
Information on buffer:
In the augentbot data directory lives a file buffer.txt, which contains pre-produced tweets. In case the full augentbot
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

    augent_constants.api.update_status(tweets[0])
    
    if create_buffers:
        augent_constants.buffer_file.write('\n' + '\n'.join(tweets[1:]))


def tweet_from_buffer() -> None:
    augent_constants.read_buffer()
    augent_constants.api.update_status(augent_constants.buffer_data.pop())
    augent_constants.buffer_file.write(''.join(augent_constants.buffer_data)[:-1])  # remove newline at end of file


def run(create_buffers: int = 0) -> None:
    try:
        followback()
    except Exception as e:
        log_info(str(e), notify=True)

    try:
        process_new_tweets()
    except Exception as e:
        log_info(str(e), notify=True)

    try:
        tweet_new(create_buffers)
    except Exception as e:
        log_info(str(e), notify=True)
        try:
            tweet_from_buffer()
        except Exception as e:
            log_info('{} in buffer'.format(str(e)), notify=True)


if __name__ == '__main__':
    import os
    if platform.system() == 'Windows':
        os.system('chcp 65001')  # fixes encoding errors on windows

    generate_tweets()
