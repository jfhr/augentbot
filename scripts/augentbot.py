import os
from pymarkovchain import MarkovChain
from nltk.corpus import gutenberg, udhr, webtext, twitter_samples
from tweet_text import make_tweet, get_plain
from timestamps import read_wo_timestamps


def generate_tweets(count=1):
    mc = MarkovChain()

    base_corpus = webtext.raw()
    base_corpus += gutenberg.raw()
    base_corpus += udhr.raw('English-Latin1')

    twitter_samples_list = twitter_samples.strings()
    base_corpus += '\n'.join([get_plain(t) for t in twitter_samples_list])

    with open(os.path.join("..", "data", "data.txt")) as file:
        collected_data = '\n'.join(read_wo_timestamps(file.readlines()))

    mc.generateDatabase(base_corpus + collected_data)

    tweets = []
    for i in range(count):
        tweets.append(make_tweet(mc.generateString()))
    
    return tweets


if __name__ == '__main__':
    '''
    When executed, the script interactively asks for the number of tweets to produce.
    That many tweets are then produced, printed out and saved to text files in the tweets directory.
    Every tweet lives in a separate text file of the form '{n}.txt', where n is a number that identifies the tweet
    internally. After creation, these files are automatically being pushed to github.
    A scheduled process hosted at integromat.com automatically gets one tweet per hour from the github repository
    and tweets it to twitter.com/augentbot. This method allows to create almost arbitrarily many tweets in advance,
    and tweet them to the right time without the need to operate an own server.    
    '''
    number_tweets = int(input('Number of tweets to produce: '))
    tweets = generate_tweets(number_tweets)

    print('\n'.join(tweets))

    with open(os.path.join("..", "tweets", "_nexttweet.txt")) as file:
        next_tweet_id = int(file.read())

    for n in range(next_tweet_id, next_tweet_id+number_tweets):
        with open(os.path.join("..", "tweets", "{}.txt".format(str(n))), 'w') as tfile:
            tfile.write(tweets[n-next_tweet_id])

    with open(os.path.join("..", "tweets", "_nexttweet.txt"), 'w') as file:
        file.write(str(next_tweet_id+number_tweets))

    # TODO: automatically push changes to github
