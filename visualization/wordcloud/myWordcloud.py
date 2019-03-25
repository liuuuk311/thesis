# Start with loading all necessary libraries
import numpy as np
import pandas as pd
import os
import sys,getopt
from wordcloud import WordCloud, ImageColorGenerator
import re


def main(argv):
    datasets = []

    # All datasets must be placed in the data/ folder
    opts, args = getopt.getopt(argv, "", ("dataset="))
    for opt, arg in opts:
        if opt == '--dataset':
            datasets.append(arg)

    if not datasets:
        datasets = os.listdir('data')


    with open("utils/stopwords-it.txt") as f:
            STOPWORDS = f.readlines()

    # you may also want to remove whitespace characters like `\n` at the end of each line
    STOPWORDS = [x.strip() for x in STOPWORDS] 

    for dataset in datasets:
        # Load in the dataframe
        df = pd.read_csv("data/" + dataset, sep=';', error_bad_lines=False)

        df.text = df.text.apply(lambda x: str(x).lower())
        df.text = df.text.apply(lambda x: str(x).replace('# ', '#'))
        df.text = df.text.apply(lambda x: re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)', '', x))
        df.text = df.text.apply(lambda x: re.sub(r'\w*\.\w*\.\w*\/\w*', '', x))


        text = " ".join(tweet for tweet in df.text)

        # Create and generate a word cloud image:
        wordcloud = WordCloud(stopwords=STOPWORDS, width=1280, height=720).generate(text)



        # Save the image in the img folder:
        wordcloud.to_file("visualization/img/" + dataset.split('.')[0] + ".png")

if __name__ == '__main__':
    main(sys.argv[1:])