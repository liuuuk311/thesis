import csv
from getRandomTweets import get_rand_tweet

import treetaggerwrapper



lemma_dict = {}

with open('utils/it.lemma.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            
            if row[4] not in lemma_dict:
                lemma_dict[row[4]] = int(row[2].replace('positive', '1').replace('negative', '-1').replace('neutral', '0'))
                # lemma_dict[row[4]] = float(row[6])


def get_polarity_score(text, debug=False):
    tagger = treetaggerwrapper.TreeTagger(TAGLANG='it')
    tags = tagger.tag_text(text)
    tags = treetaggerwrapper.make_tags(tags)


    score = 0
    n = 0
    for w in tags:
        if w.lemma in lemma_dict:
            score += int(lemma_dict[w.lemma])
            n += 1
            if debug:
                print('Word: ' + w.lemma + ' Score: ' + str(lemma_dict[w.lemma]))
    
    return score/len(text.split()), score/n




if __name__ == "__main__":

    
    tweet = get_rand_tweet()['text']
    tweet = tweet.replace('"', '')

    tweet = tweet.lower()
    print(tweet)
    print(get_polarity_score(tweet, debug=True))
