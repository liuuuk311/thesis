import csv
# from getRandomTweets import get_rand_tweet
import logging
import treetaggerwrapper


logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename='polarity.log', level=logging.INFO)

lemma_dict = {}

with open('utils/it.lemma.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            
            if row[4] not in lemma_dict:
                lemma_dict[row[4]] = int(row[2].replace('positive', '1').replace('negative', '-1').replace('neutral', '0'))
                # lemma_dict[row[4]] = float(row[6])


def get_polarity_score(text):
    if len(text) == 0:
       return 0

    tagger = treetaggerwrapper.TreeTagger(TAGLANG='it')
    tags = tagger.tag_text(text)
    tags = treetaggerwrapper.make_tags(tags)


    score = 0
    n = 0
    for w in tags:
        logging.info("Check if %s is in the dictionary", w)
        if isinstance(w, treetaggerwrapper.Tag):
            if w.lemma in lemma_dict:
                score += int(lemma_dict[w.lemma])
                n += 1
                logging.info('Word: ' + w.lemma + ' Score: ' + str(lemma_dict[w.lemma]))
    
    return score/len(text.split())




if __name__ == "__main__":

    tweet = 'Questa è un prova, voglio vedere se capisce che fa schifo'

    tweet = tweet.lower()
    print(tweet)
    print(get_polarity_score(tweet))
