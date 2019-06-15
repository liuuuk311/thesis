from getRandomTweets import get_rand_tweet
from flask import Flask
from flask import request, render_template
import pandas as pd


import csv

from flask import session, redirect, url_for, escape




filename = 'data/barcone15-16_copy.csv'

app = Flask(__name__)
app.config['DEBUG'] = True


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

df = pd.read_csv(filename, sep=';')
df.id = df.id.map(lambda x: '{:.0f}'.format(x))
df.id = df.id.astype(str)
df['annotatation1'] = ""
df['annotatation2'] = ""
df['annotatation3'] = ""
df['annotatation4'] = ""
df['annotatation5'] = ""
df['annotatorCount'] = 0
df.to_csv(filename, sep=';', index=False)

@app.route('/', methods=['GET', 'POST'])
def index():

    df = pd.read_csv(filename, sep=';')
    df.id = df.id.map(lambda x: '{:.0f}'.format(x))
    df.id = df.id.astype(str)

    myprgoress = 0
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
        count = df.loc[df.id == myId]['annotatorCount'].values[0]
        colname = 'annotatation' + str(count)
        df.loc[df.id == myId, colname] = polarity

        session[session['userId']] += 1
        print(session[session['userId']] )
        myprgoress = int((session[session['userId']] / 25 ) * 100)
        
    df.to_csv(filename, sep=';', index=False)
    myrow = df[df['annotatorCount'] < 5].sample(1)
    
    if 'userId' in session and myprgoress <= 100:
        return render_template('tweet.html', tweet=myrow.to_dict('records')[0], progress=myprgoress)
    elif 'userId' in session and myprgoress > 100:
        return redirect('/thank-you')
    else:
        return redirect('/start')

    # 


@app.route('/start', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['userId'] = request.form['userId']
        session[request.form['userId']] = 0
        return redirect(url_for('index'))
    return render_template('welcome.html')


@app.route('/thank-you')
def logout():
    # remove the username from the session if it's there
    session.pop('userId', None)
    return render_template('thank-you.html')

if __name__ == '__main__':
    app.run(debug=True)
