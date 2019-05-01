import requests
from bs4 import BeautifulSoup
import json

username = 'matteosalvinimi'
tweetId = '1123286616896933891'


baseURL = 'https://twitter.com/' + username + '/status/' + tweetId
getNextURL = 'https://twitter.com/i/' + username + '/conversation/' + tweetId + \
    '?include_available_features=1&include_entities=1&reset_error_state=false&max_position='


def get_retweet(soup, user):
    retweets = soup.find_all('div', {'class': 'ReplyingToContextBelowAuthor'})

    res = []

    for retweet in retweets:
        reply_to = retweet.find('a').get('href')
        if user in reply_to:
            res.append(retweet.parent.find(
                'p', {'class': 'tweet-text'}).get_text())

    return res


if __name__ == "__main__":
    count = 0
    res = requests.get(baseURL)
    soup = BeautifulSoup(res.text, 'html.parser')

    retweets_list = get_retweet(soup, username)

    div = soup.find('div', {'class': 'stream-container'})
    min_pos = div['data-min-position']

    while True:
        res = requests.get(getNextURL + min_pos)
        res = json.loads(res.text)
        min_pos = res['min_position']
        if not res['has_more_items'] or min_pos is None:
            break

        soup = BeautifulSoup(res['items_html'], 'html.parser')
        retweets_list += get_retweet(soup, username)

for retweet in retweets_list:
    print(retweet)
