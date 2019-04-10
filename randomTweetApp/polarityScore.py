import csv
from getRandomTweets import get_rand_tweet

lemma_dict = {}

with open('utils/it.lemma.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if row[4] not in lemma_dict:
                lemma_dict[row[4]] = int(row[2].replace('positive', '1').replace('negative', '-1').replace('neutral', '0'))


def get_polarity_score(text):
    score = 0
    for w in text.split():
        if w in lemma_dict:
            score += lemma_dict[w]
    
    return score/len(text.split())



if __name__ == "__main__":
    tweet = get_rand_tweet()
    tweet = tweet.replace('"', '')

    tweet = tweet.lower()
    print(tweet)
    print(get_polarity_score(tweet))