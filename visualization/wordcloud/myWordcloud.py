# Start with loading all necessary libraries
import numpy as np
import pandas as pd
from os import path
from PIL import Image
import sys,getopt
from wordcloud import WordCloud, ImageColorGenerator
import re


def main(argv):
    if len(argv) == 0:
        print('You must pass some parameters.')
        return

    # Default dataset
    dataset = "immigrati15-16"

    # All datasets must be placed in the data/ folder
    opts, args = getopt.getopt(argv, "", ("dataset="))
    for opt, arg in opts:
        if opt == '--dataset':
            dataset = arg


        # Load in the dataframe
        df = pd.read_csv("data/" + dataset + ".csv", sep=';', error_bad_lines=False)

        df.text = df.text.apply(lambda x: x.lower())
        df.text = df.text.apply(lambda x: x.replace('# ', '#'))
        df.text = df.text.apply(lambda x: re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=]*)', '', x))
        df.text = df.text.apply(lambda x: re.sub(r'\w*\.\w*\.\w*\/\w*', '', x))


        text = " ".join(tweet for tweet in df.text)


        with open("data/stopwords-it.txt") as f:
            STOPWORDS = f.readlines()


        # you may also want to remove whitespace characters like `\n` at the end of each line
        STOPWORDS = [x.strip() for x in STOPWORDS] 


        # Create and generate a word cloud image:
        wordcloud = WordCloud(stopwords=STOPWORDS, width=1280, height=720).generate(text)



        # Save the image in the img folder:
        wordcloud.to_file("visualization/img/" + dataset + ".png")

if __name__ == '__main__':
    main(sys.argv[1:])