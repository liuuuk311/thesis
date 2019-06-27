# from getRandomTweets import get_rand_tweet
from flask import Flask
from flask import request, render_template
from flask import session, redirect, url_for, escape
import pandas as pd
import numpy as np
import csv


filename = './data/dataset.csv'

app = Flask(__name__)
app.config['DEBUG'] = True

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Just the first time
if app.config['DEBUG']:
    df = pd.read_csv(filename, sep=';')
    df['isValid'] = 1
    df['annotatorCount'] = np.nan
    for i in range(1, 6):
        df['annotation' + str(i)] = np.nan
    df.annotatorCount.fillna(0, inplace=True)
    df.to_csv(filename, sep=';', index=False)


@app.route('/', methods=['GET', 'POST'])
def index():

    df = pd.read_csv(filename, sep=';')
    df.id = df.id.map(lambda x: '{:.0f}'.format(x))
    df.id = df.id.astype(str)

    myprogress = 0
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
        df.loc[df.id == myId, 'isValid'] = isValid
        count = df.loc[df.id == myId]['annotatorCount'].values[0]
        colname = 'annotation' + str(int(count))
        df.loc[df.id == myId, colname] = polarity

        session[session['userId'] + '-ans'].append(myId)
        session[session['userId'] + '-ans'] = session[session['userId'] + '-ans']

        myprogress = int((len(session[session['userId'] + '-ans']) / 30) * 100)

    if not app.config['DEBUG']:
        df.to_csv(filename, sep=';', index=False)

    # Subset of tweets which the user hasn't annotated yet
    if 'userId' in session and len(session[session['userId'] + '-ans']) > 0:
        df = df[~df['id'].isin(session[session['userId'] + '-ans'])]

    # Subset of tweets which have less then 5 annoatation and have some text
    df = df[(df['annotatorCount'] < 5 & ~df['text'].isna()) & df['isValid'] != 0]

    if len(df.index) == 0:
        return redirect('/end')  # We have no more tweet to show at this user

    myrow = df.sample(1)

    print(myrow['parentText'])

    if 'userId' in session and myprogress < 100:
        return render_template('tweet.html', tweet=myrow.to_dict('records')[0], progress=myprogress)
    elif 'userId' in session and myprogress >= 100:
        return redirect('/thank-you')
    else:
        return redirect('/start')


@app.route('/start', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['userId'] = request.form['userId']
        session[request.form['userId'] + '-ans'] = []
        return redirect(url_for('index'))
    return render_template('welcome.html')


@app.route('/thank-you')
def logout():
    # remove the username from the session if it's there
    if 'userId' in session:
        clearSession()
        return render_template('thank-you.html')
    else:
        return redirect('/start')

@app.route('/end')
def end():
    clearSession()
    return render_template('end.html')


@app.route('/stats')
def stats():
    df = pd.read_csv(filename, sep=';')
    total_count = len(df)
    done_count = len(df[df['annotatorCount'] > 0])
    todo_count = len(df[df['annotatorCount'] == 0])
    people_done_count = round(len(df[df['annotatorCount'] > 0])/30)
    people_todo_count = round(( len(df[df['annotation1'].isna()]) +
                                len(df[df['annotation2'].isna()]) +
                                len(df[df['annotation3'].isna()]) +
                                len(df[df['annotation4'].isna()]) +
                                len(df[df['annotation5'].isna()])) /30)

    return render_template('stats.html',    total_count=total_count, 
                                            done_count=done_count, 
                                            todo_count=todo_count, 
                                            people_done_count=people_done_count, 
                                            people_todo_count=people_todo_count)


# Helper
def clearSession():
    session.pop(session['userId'] + '-ans', None)
    session.pop('userId', None)


if __name__ == '__main__':
    app.run(debug=True)
