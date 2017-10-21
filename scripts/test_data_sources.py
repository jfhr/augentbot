#! python3
from timestamps import read_wo_timestamps
from tweet_text import get_plain_text, get_viable_text, grammar_check
from augentbot import generate_tweets, DATA
from pymarkovchain import MarkovChain
from nltk.corpus import udhr, brown, gutenberg, twitter_samples
import os

base_corpus = str()
base_corpus += open('C:/Users/ajm-f/augentbot/corpus/udhr.txt', 'r').read()
base_corpus += open('C:/Users/ajm-f/augentbot/corpus/twitter_samples.txt', 'r').read()


collected_data = str()
collected_data += '\n'.join(read_wo_timestamps(open('C:/Users/ajm-f/augentbot/data/data.txt').readlines()))

mc = MarkovChain()
mc.generateDatabase(base_corpus + collected_data, n=5)
tweets = generate_tweets(mc=mc, count=8)
