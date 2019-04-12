import csv
from getRandomTweets import get_rand_tweet

lemma_dict = {}

with open('utils/sentix') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            
            if row[4] not in lemma_dict:
                # lemma_dict[row[4]] = int(row[2].replace('positive', '1').replace('negative', '-1').replace('neutral', '0'))
                lemma_dict[row[4]] = float(row[6])


def get_polarity_score(text, debug=False):
    score = 0
    for w in text.split():
        if w in lemma_dict:
            score += int(lemma_dict[w])
            if debug:
                print('Word: ' + w + ' Score: ' + str(lemma_dict[w]))
    
    return score/len(text.split())




if __name__ == "__main__":
    tweet = get_rand_tweet()['text']
    tweet = tweet.replace('"', '')

    tweet = tweet.lower()
    print(tweet)
    print(get_polarity_score(tweet, debug=True))