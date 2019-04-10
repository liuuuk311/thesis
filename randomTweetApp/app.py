from getRandomTweets import get_rand_tweet
from flask import Flask
from flask import request, render_template

app = Flask(__name__)
app.config['DEBUG'] = True



@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        print(request.form['submit_button'])
    else:
        print('Get')
    

    return render_template('tweet.html', tweet=get_rand_tweet())


if __name__ == '__main__':
    app.run(debug=True)