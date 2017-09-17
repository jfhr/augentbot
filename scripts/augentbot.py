import os
from pymarkovchain import MarkovChain
from nltk.corpus import gutenberg, udhr, webtext, twitter_samples
from tweet_texts import filter_tweet
from timestamps import read_wo_timestamps

def generate_tweets(count):
    mc = MarkovChain()

    base_corpus = webtext.raw()
    base_corpus += gutenberg.raw()
    base_corpus += udhr.raw('English-Latin1')
    base_corpus += [filter_tweet(t) for t in twitter_samples.strings()]

    collected_data = read_wo_timestamps(os.path.join("..", "data", "data.txt"))

    mc.generateDatabase(base_corpus + collected_data)

    tweets = []
    for i in range(count):
        tweets.append(mc.generateString())
    
    return tweets

if __name__ == '__main__':
    print('\n'.join(generate_tweets(3)))
