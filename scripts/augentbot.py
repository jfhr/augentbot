#! python3

import os
import tweepy
import datetime
from pymarkovchain import MarkovChain
from nltk.corpus import gutenberg, udhr, webtext, twitter_samples

from tweet_text import make_tweet, get_plain, viable, get_weight
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

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


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
    with open(os.path.join('..', "data", "log.txt"), 'a') as file:
        file.write(add_timestamp(entry) + '\n')
    print(entry)
    if notify:
        notify_me(entry)


def add_data(entry, weight=1):
    for i in range(weight):
        with open(os.path.join('..', 'data', 'data.txt'), 'a') as file:
            file.write(add_timestamp(entry) + '\n')


def process_new_tweets():
    """
    Gets new tweets from the augentbot home timeline, checks every tweet for viability, and adds that tweet to
    the data log. If a tweet has a high weight (many likes and retweets compared to the author's follower count),
    it is being added more often.
    Only tweets older than 2 days are being processed. To make sure each tweet isn't being processed more than once,
    the id of the youngest tweet that has been processed is being stored during every run.
    """
    p = 0
    logged_last_id = False

    with open(os.path.join('..', 'data', '_lastid.txt')) as file:
        last_id = int(file.read())
  
    last_id_file = open(os.path.join('..', 'data', '_lastid.txt'), 'w')
    data_file = open(os.path.join('..', 'data', 'data.txt'), 'a')

    while True:
        new_tweets = api.home_timeline(count=200, page=p)

        # limit this process to a maximum number of pages
        if p == 25:
            log_info('Reached limit of tweets to process.')
            data_file.close()
            last_id_file.write(new_tweets[0].id)
            last_id_file.close()
            return

        # skip tweets that aren't older than two days
        for t in new_tweets:
            if t.created_at > datetime.datetime.now() - datetime.timedelta(days=2):
                continue

            elif t.id <= last_id:
                log_info('All tweets processed')
                data_file.close()
                last_id_file.write(t.id)
                last_id_file.close()
                return

            else:
                if viable(t):
                    log_info("Processing tweet '{0}' ... viable".format(get_plain(t.text)))
                    add_data(get_plain(t.text), get_weight(t))
                else:
                    log_info("Processing tweet '{0}' ... not viable".format(get_plain(t.text)))
        p += 1


def generate_tweets(count=1):
    mc = MarkovChain()

    base_corpus = ''
    base_corpus += webtext.raw()
    base_corpus += gutenberg.raw()
    base_corpus += udhr.raw('English-Latin1')

    twitter_samples_list = twitter_samples.strings()
    base_corpus += '\n'.join([get_plain(t) for t in twitter_samples_list])

    with open(os.path.join('..', "data", "data.txt")) as file:
        collected_data = '\n'.join(read_wo_timestamps(file.readlines()))

    mc.generateDatabase(base_corpus + collected_data)

    tweets = []
    for i in range(count):
        tweet = make_tweet(mc.generateString())
        log_info("Added tweet '{}'".format(tweet))
        tweets.append(tweet)
    
    return tweets


def add_tweets_interactive():
    """
    When executed, this method interactively asks for the number of tweets to produce.
    That many tweets are then produced, printed out and saved to text files in the tweets directory.
    Every tweet lives in a separate text file of the form '{n}.txt', where n is a number that identifies the tweet
    internally. After creation, these files are automatically being pushed to github.
    A scheduled process hosted at integromat.com automatically gets one tweet per hour from the github repository
    and tweets it to twitter.com/augentbot . This method allows to create almost arbitrarily many tweets in advance,
    and tweet them to the right time without the need to operate an own server.
    """
    number_tweets = int(input('Number of tweets to produce: '))
    tweets = generate_tweets(number_tweets)

    with open(os.path.join('..', "tweets", "_nexttweet.txt")) as file:
        next_tweet_id = int(file.read())

    for n in range(next_tweet_id, next_tweet_id+number_tweets):
        with open(os.path.join('..', "tweets", "{}.txt".format(str(n))), 'w') as tfile:
            tfile.write(tweets[n-next_tweet_id])

    with open(os.path.join('..', "tweets", "_nexttweet.txt"), 'w') as file:
        file.write(str(next_tweet_id+number_tweets))


if __name__ == '__main__':
    os.system('chcp 65001')
    process_new_tweets()
    add_tweets_interactive()
