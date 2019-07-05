# from getRandomTweets import get_rand_tweet
from flask import Flask
from flask import request, render_template
from flask import session, redirect, url_for, escape
import pandas as pd
import numpy as np
import csv

import os
import psycopg2
from sqlalchemy import create_engine

# os.environ["DATABASE_URL"] = "bsquuuxfulbdet:74a62e2386f93628d98bdfe28818b842264aefff63f743313c2b7ff8e09b138d@ec2-54-228-246-214.eu-west-1.compute.amazonaws.com:5432/dlb44esdgbdtv"
DATABASE_URL = os.environ['DATABASE_URL']

engine = create_engine(DATABASE_URL,pool_size=10, max_overflow=20)

filename = './data/dataset.csv'

app = Flask(__name__)
app.config['DEBUG'] = False
create = False

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Just the first time
if app.config['DEBUG'] and create:
    print('Reading the file...')
    df = pd.read_csv(filename, sep=';')
    df['isValid'] = 1
    df['annotatorCount'] = np.nan
    for i in range(1, 6):
        df['annotation' + str(i)] = np.nan
    df.annotatorCount.fillna(0, inplace=True)
    df.to_csv(filename, sep=';', index=False)
    df.to_sql('dataset', engine, if_exists='replace')



@app.route('/', methods=['GET', 'POST'])
def index():

    # df = pd.read_csv(filename, sep=';')
    df = pd.read_sql_table('dataset', engine)
    df.id = df.id.map(lambda x: '{:.0f}'.format(x))
    df.id = df.id.astype(str)

    myprogress = 0
    if request.method == 'POST':
        isValid = 1

        value = request.form['submit_button']
        if value.lower() == 'positiva':
            polarity = 1
        elif value.lower() == 'neutra':
            polarity = 0
        elif value.lower() == 'negativa':
            polarity = -1
        else:
            isValid = 0
            polarity = 'NULL'

        myId = request.form['id'].replace('"', '')

        df.loc[df.id == myId, 'annotatorCount'] += 1
        df.loc[df.id == myId, 'isValid'] = isValid
        count = df.loc[df.id == myId]['annotatorCount'].values[0]
        colname = 'annotation' + str(int(count))
        df.loc[df.id == myId, colname] = polarity

        session[session['userId'] + '-ans'].append(myId)
        session[session['userId'] + '-ans'] = session[session['userId'] + '-ans']

        myprogress = int((len(session[session['userId'] + '-ans']) / 30) * 100)


        if not app.config['DEBUG'] and count <= 5:
            # df.to_csv(filename, sep=';', index=False)
            connection = engine.connect()
            sql_stmt = """
            UPDATE dataset
                SET "annotatorCount" = {0},
                    "isValid" = {1},
                    "{2}" = {3}
            WHERE id = {4}
            """.format(df.loc[df.id == myId, 'annotatorCount'].values[0], 
                        df.loc[df.id == myId, 'isValid'].values[0], 
                        colname, 
                        df.loc[df.id == myId, colname].values[0], 
                        myId)
            connection.execute(sql_stmt)
            connection.close()
            

    # Subset of tweets which the user hasn't annotated yet
    if 'userId' in session and len(session[session['userId'] + '-ans']) > 0:
        df = df[~df['id'].isin(session[session['userId'] + '-ans'])]

    # Subset of tweets which have less then 5 annoatation and have some text
    df = df[(df['annotatorCount'] <= 5 & ~df['text'].isna()) & df['isValid'] != 0]

    if len(df.index) == 0:
        return redirect('/end')  # We have no more tweet to show at this user

    myrow = df.sample(1)

    

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
    if 'userId' in session:
        clearSession()
        return render_template('end.html')
    else:
        return redirect('/start')
    


@app.route('/stats')
def stats():
    # df = pd.read_csv(filename, sep=';')
    df = pd.read_sql_table('dataset', engine)
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
