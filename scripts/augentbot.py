#! python3

import os
import platform
import tweepy
import datetime
from pymarkovchain import MarkovChain
from nltk.corpus import gutenberg, udhr, webtext, twitter_samples

from tweet_text import make_tweet, get_plain, viable, get_weight, IGNORED_USERS
from timestamps import read_wo_timestamps, add_timestamp

TWITTER_CONSUMER_KEY = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials',
                                         'twitter_consumer_key')).read()
TWITTER_CONSUMER_SECRET = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials',
                                            'twitter_consumer_secret')).read()
TWITTER_ACCESS_TOKEN = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials',
                                         'twitter_access_token')).read()
TWITTER_ACCESS_TOKEN_SECRET = open(os.path.join(os.path.expanduser('~'), 'augentbot', 'credentials',
                                                'twitter_access_token_secret')).read()

HOST_NAME = '_jfde'

DATA = os.path.join(os.path.expanduser('~'), 'augentbot', 'data')

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# venv_path = os.path.join(os.path.expanduser('~'), '.virtualenvs', 'augentbot')
# automatic virtualenv activation is disabled for now


def confirm(prompt='Confirm this action?'):
    prompt = prompt.strip()
    if not prompt.endswith('?'):
        prompt += '?'
    prompt += ' (y/n): '
    return input(prompt).lower().strip() == 'y'


def notify_me(text):
    """
    send a message to the user specified as HOST_NAME. Messages longer than 10000
    characters will be split in submessages due to twitter limits
    """
    for subtext in [text[i:i+10000] for i in range(0, len(text), 10000)]:
        try:
            api.send_direct_message(screen_name=HOST_NAME, text=subtext)
        except tweepy.TweepError as e:
            log_info("{0} when trying to send the following dm:\n    '{1}'".format(e, text))


def log_info(entry, notify=False):
    """
    Attaches a timestamp with the current time to the entry,
    prints the entry and saves it in the log.txt file of the data directory.
    It notify is true, the entry with the add_timestamp will be sent to the
    user specified as HOST_NAME via twitter dm. This requires that the user
    has allowed receiving dms from this account
    """
    with open(os.path.join(DATA, "log.txt"), 'a') as file:
        file.write(add_timestamp(entry) + '\n')
    print(entry)
    if notify:
        notify_me(entry)


def add_data(entry, weight=1):
    for i in range(weight):
        with open(os.path.join(DATA, 'data.txt'), 'a') as file:
            file.write(add_timestamp(entry) + '\n')


def followback():
    followers = [follower.screen_name for follower in api.followers()]
    # follow back
    followings = [following.screen_name for following in api.friends()]
    for follower in followers:
        if follower not in followings + IGNORED_USERS:
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
        if following not in followers + IGNORED_USERS:
            try:
                api.destroy_friendship(following)
                log_info('unfollowed @{0}'.format(following))
            except tweepy.RateLimitError:
                log_info('Rate limit exceeded.', True)
                break
            except tweepy.TweepError:
                log_info("Couldn't follow @{0}".format(following))


def process_new_tweets():
    """
    Gets new tweets from the augentbot home timeline, checks every tweet for viability, and adds that tweet to
    the data log. If a tweet has a high weight (many likes and retweets compared to the author's follower count),
    it is being added more often.
    Only tweets older than 2 days are being processed. To make sure each tweet isn't being processed more than once,
    the id of the youngest tweet that has been processed is being stored during every run.
    """

    with open(os.path.join(DATA, '_lastid.txt')) as file:
        last_id = int(file.read())
  
    last_id_file = open(os.path.join(DATA, '_lastid.txt'), 'w')

    def process_tweet(t):
        if viable(t):
            log_info("Processing tweet {0}: '{1}' ... viable".format(t.author.screen_name, get_plain(t.text)))
            add_data(get_plain(t.text), get_weight(t))
        else:
            log_info("Processing tweet {0}: '{1}' ... not viable".format(t.author.screen_name, get_plain(t.text)))

    def close(last_id, reason=None, notify_me=False):
            if reason is not None:
                log_info(reason, notify_me)
            last_id_file.write(str(last_id))
            last_id_file.close()
            return

    for p in range(6):    # limit this process to a maximum number of pages
        new_tweets = api.home_timeline(count=200, page=p)
        if len(new_tweets) > 0:
            last_id = new_tweets[-1].id
        else:
            close(last_id, reason='Reached void page.')
            # Respects tweepy pagination limits

        for t in new_tweets:
            # skip tweets that aren't older than two days
            if t.created_at > datetime.datetime.now() - datetime.timedelta(days=2):
                continue

            # if a tweet is older than the youngest tweet processed last time, end the execution
            elif t.id <= last_id:
                close(t.id, 'All tweets processed.')
                return

            # if a tweet is in the range of tweets to process, check if it is viable
            else:
                process_tweet(t)

    close(new_tweets[0].id, 'Reached limit of tweets to process.')
    return


def generate_tweets(count=1):
    mc = MarkovChain()

    base_corpus = ''
    base_corpus += webtext.raw()
    base_corpus += gutenberg.raw()
    base_corpus += udhr.raw('English-Latin1')

    twitter_samples_list = twitter_samples.strings()
    base_corpus += '\n'.join([get_plain(t) for t in twitter_samples_list])

    with open(os.path.join(DATA, "data.txt")) as file:
        collected_data = '\n'.join(read_wo_timestamps(file.readlines()))

    mc.generateDatabase(base_corpus + collected_data)

    tweets = []
    for i in range(count):
        tweet = make_tweet(mc.generateString())
        log_info("Added tweet '{}'".format(tweet))
        tweets.append(tweet)

    return tweets


def tweet_new():
    api.update_status(generate_tweets()[0])


def tweet_from_buffer():
    with open(os.path.join(DATA, 'buffer.txt')) as file:
        buffer = file.readlines()

    api.update_status(buffer.pop())

    with open(os.path.join(DATA, 'buffer.txt'), 'w') as file:
        file.write('\n'.join(buffer))


def run():
    # if os.path.exists(venv_path):
    #     os.system(os.path.join(venv_path, 'activate'))
    if platform.system() == 'Windows':
        os.system('chcp 65001')  # fixes encoding errors on windows
    os.system('git pull')

    try:
        followback()
        process_new_tweets()
        tweet_new()
    except Exception as e:
        log_info(e, notify=True)
        try:
            tweet_from_buffer()
        except Exception as e:
            log_info('{} in buffer'.format(str(e), notify=True)


def run_scheduled():
    try:
        followback()
        process_new_tweets()
        tweet_new()
    except Exception as e:
        log_info(e, notify=True)
        try:
            tweet_from_buffer()
        except Exception as e:
            log_info('{} in buffer'.format(str(e), notify=True)

    
if __name__ == '__main__':
    if input('Run now? (y/n)').lower().strip() == 'y':
        run()

