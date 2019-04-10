import random
import csv
import glob

from textCleaner import clean

files = [f for f in glob.glob("data/*.csv", recursive=False)]
# Contiene tweet stranieri
files.remove('data/clandestini15-16.csv')

def get_tweet_dict(text):
    metadata = ['username', 'date', 'retweets', 'favorites', 'text', 'geo', 'mentions', 'hashtags', 'id', 'permalink']
   
    tweet = {}
    for i, m in enumerate(metadata):
        tweet[m] = text[i]

    return tweet

def get_rand_tweet(debug=False):
    rand_file = files[random.randrange(len(files))]

    filesize = sum(1 for line in open(rand_file)) #size of the really big file

    offset = random.randrange(filesize)

    f = open(rand_file)
    f.seek(offset)                  #go to random position
    f.readline()                    # discard - bound to be partial line
    rand_line = f.readline()        # bingo!

    # extra to handle last/first line edge cases
    if len(rand_line) == 0:         # we have hit the end
        f.seek(1)
        rand_line = f.readline()    # so we'll grab the first line instead
    

    splitted = rand_line.split(';')

    if debug: 
        print(splitted)

    splitted[4] = clean(splitted[4])
    
    tweet = get_tweet_dict(splitted)
    
    return tweet

if __name__ == "__main__":
    print(get_rand_tweet())