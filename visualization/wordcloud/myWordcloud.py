# Start with loading all necessary libraries
import numpy as np
import pandas as pd
from os import path
from PIL import Image
import sys,getopt
from wordcloud import WordCloud, ImageColorGenerator

try:
    # Default dataset
    dataset = "salvini15-16"

    # All datasets must be placed in the data/ folder
    opts, args = getopt.getopt(argv, "", ("dataset="))
    for opt, arg in opts:
        if opt == 'dataset':
            dataset = arg
    

    # Load in the dataframe
    df = pd.read_csv("data/" + dataset + ".csv", sep=';')

    df.text = df.text.apply(lambda x: x.lower())


    text = " ".join(tweet for tweet in df.text)

    with open("data/stopwords-it.txt") as f:
        STOPWORDS = f.readlines()


    # you may also want to remove whitespace characters like `\n` at the end of each line
    STOPWORDS = [x.strip() for x in STOPWORDS] 

    STOPWORDS += ['facebook', 'twitter', 'https', 'www', 'com', 'pic']

    # Create and generate a word cloud image:
    wordcloud = WordCloud(stopwords=STOPWORDS, width=1280, height=720).generate(text)



    # Save the image in the img folder:
    wordcloud.to_file("visualization/img/" + dataset + ".png")

except:
    print('Argument parser error, please try again')