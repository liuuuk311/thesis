# Utilis
import os
from json import dumps

# Flask
from flask import Flask
from flask import Flask, g, Response, request, render_template, session, redirect, url_for

# Database
import psycopg2
from sqlalchemy import create_engine
from neo4j import GraphDatabase, basic_auth

# Misc
import pandas as pd


# Get environment variables
GRAPHENEDB_URL = os.environ.get("GRAPHENEDB_BOLT_URL")
GRAPHENEDB_USER = os.environ.get("GRAPHENEDB_BOLT_USER")
GRAPHENEDB_PASS = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

# Get a connection to the Graph Database
driver = GraphDatabase.driver(GRAPHENEDB_URL, auth=basic_auth(GRAPHENEDB_USER, GRAPHENEDB_PASS))


# Get environment variable
# DATABASE_URL = os.environ.get('DATABASE_URL')

# Get a connection to Relation Database
# sql_engine = create_engine(DATABASE_URL,pool_size=10, max_overflow=20)


# Define the app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = True

# Get the session on DB
def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

# Close the existing session
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()

@app.route('/start', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['userId'] = request.form['userId']
        session[session['userId'] + '-ans'] = []
    
        return redirect(url_for('get_index'))
    return render_template('welcome.html')

# Index route
@app.route('/', methods=['GET']) 
def get_index():
    if 'userId' in session:
        
        return redirect('/next_tweet')
    # elif 'userId' in session and myprogress >= 100:
    #     return redirect('/thank-you')
    else:
        return redirect('/start')

@app.route("/save", methods=['POST'])
def save():
    if 'userId' in session:
        
        tweet_id = request.form['id']
        tweet_polarity = int(request.form['polarity'])

    
        str_polarity = ""
        if len(session[session['userId'] + '-ans']) % 4 == 0:
            session['mainPolarity'] = tweet_polarity
        else:
            tweet_polarity = tweet_polarity * session['mainPolarity'] 
            str_polarity = 'DISAGREE' if tweet_polarity < 0 else 'AGREE'

        session[session['userId'] + '-ans'].append(tweet_id)
        session[session['userId'] + '-ans'] = session[session['userId'] + '-ans']
        
        query = """
        MATCH (a:Tweet)-[r:REPLIES]->(b:Tweet)
        WHERE a.id = {tweet_id}
        SET r.polarity = {polarity}
        """

        db = get_db()
        query_result = db.run(query, tweet_id=tweet_id, polarity=str_polarity)
        return redirect('/next_tweet')
    else:
        return redirect('/start')
        

@app.route('/next_tweet', methods=['GET']) 
def get_next_tweet():
    
    if 'userId' in session:
        
        query = """
        MATCH (a:Tweet)-[r:REPLIES]->(b:Tweet)
        WHERE NOT EXISTS (r.polarity)
        RETURN a.id, a.text, r.polarity, b.id, b.text
        ORDER BY a.favouriteCount DESC
        LIMIT 1
        """#.format(session[session['userId'] + '-ans'])

        
        db = get_db()
        query_result = db.run(query) 
        result = query_result.data()
        

        if len(session[session['userId'] + '-ans']) % 4 != 0:
            tweet_dict = {'question': 'Rispetto a questa risposta', 'tweet' : {'id': result[0]['a.id'], 'text': result[0]['a.text']}}
        else:
            tweet_dict = {'question': 'Rispetto a questa tweet', 'tweet' : {'id': result[0]['b.id'], 'text': result[0]['b.text']}}

        # return Response(dumps(tweet_dict), mimetype="application/json")
        return render_template('tweet.html', data=tweet_dict)
    else:
        return redirect('/start')


@app.route('/thank-you')
def logout():
    # remove the username from the session if it's there
    if 'userId' in session:
        clearSession()
        return render_template('thank-you.html')
    else:
        return redirect('/start')


# Helper
def clearSession():
    session.pop(session['userId'] + '-ans', None)
    session.pop('userId', None)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)