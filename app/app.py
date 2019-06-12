from getRandomTweets import get_rand_tweet
from flask import Flask
from flask import request, render_template
import pandas as pd


import csv

filename = 'data/barcone15-16_copy.csv'

app = Flask(__name__)
app.config['DEBUG'] = True


df = pd.read_csv(filename, sep=';')
df.id = df.id.map(lambda x: '{:.0f}'.format(x))
df.id = df.id.astype(str)
df['annotatorCount'] = 0
df.to_csv(filename, sep=';', index=False)

@app.route('/', methods=['GET', 'POST'])
def index():

    df = pd.read_csv(filename, sep=';')
    df.id = df.id.map(lambda x: '{:.0f}'.format(x))
    df.id = df.id.astype(str)

    if request.method == 'POST':
        isValid = 1

        value = request.form['submit_button']
        if value.lower() == 'positivo':
            polarity = 1
        elif value.lower() == 'neutro':
            polarity = 0
        elif value.lower() == 'negativo':
            polarity = -1
        else:
            isValid = 0
            polarity = ''

        myId = request.form['id'].replace('"', '')

        df.loc[df.id == myId, 'annotatorCount'] += 1

    
        
    df.to_csv(filename, sep=';', index=False)
    myrow = df[df['annotatorCount'] < 5].sample(1)

  

    return render_template('tweet.html', tweet=myrow.to_dict('records')[0])


# @app.route('/', methods=['GET', 'POST'])
# def index():

#     if request.method == 'POST':
#         isValid = 1

#         value = request.form['submit_button']
#         if value.lower() == 'positivo':
#             polarity = 1
#         elif value.lower() == 'neutro':
#             polarity = 0
#         elif value.lower() == 'negativo':
#             polarity = -1
#         else:
#             isValid = 0
#             polarity = ''

#         metadata = ['username', 'date', 'retweets', 'favorites', 'text', 'geo', 'mentions', 'hashtags', 'id', 'permalink']
#         row = []
#         for m in metadata:
#             row.append(request.form[m])

#         row.append(polarity)
#         row.append(isValid)

#         with open('data/final.csv', mode='a') as csv_file:
#             writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#             writer.writerow(row)

#     else:
#         print('Get')
    

#     return render_template('tweet.html', tweet=get_rand_tweet())


if __name__ == '__main__':
    app.run(debug=True)
