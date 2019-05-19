import requests
from bs4 import BeautifulSoup
import json
import logging
import csv

logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename='replies.log', level=logging.INFO)


def get_reply(soup, user):
    replies = soup.find_all('div', {'class': 'ReplyingToContextBelowAuthor'})

    res = []

    for reply in replies:
        reply_to = reply.find('a').get('href')
        logging.info('Checking message replies to ' + user)
        if user in reply_to:
            logging.info('New reply found')
            res.append(reply.parent.find(
                'p', {'class': 'tweet-text'}).get_text())

    return res




def extract_replies(username, statusId):

    baseURL = 'https://twitter.com/' + username + '/status/' + statusId
    getNextURL = 'https://twitter.com/i/' + username + '/conversation/' + statusId + '?include_available_features=1&include_entities=1&reset_error_state=false&max_position='

    logging.info('Getting ' + baseURL)

    count = 0
    res = requests.get(baseURL)
    soup = BeautifulSoup(res.text, 'html.parser')

    replies_list = get_reply(soup, username)
    logging.info('Reply list ' + str(len(replies_list)))

    div = soup.find('div', {'class': 'stream-container'})
    min_pos = div['data-min-position']

    
    while min_pos is not None:
        logging.info('Looking for next data. Min position ' + str(min_pos))
        logging.info('Getting ' + getNextURL + min_pos)
        res = requests.get(getNextURL + min_pos)
        res = json.loads(res.text)
        min_pos = res['min_position']

        soup = BeautifulSoup(res['items_html'], 'html.parser')
        replies_list += get_reply(soup, username)

        logging.info('Reply list ' + str(len(replies_list)))

    return replies_list

if __name__ == "__main__":
    userId = 'matteosalvinimi'
    statusId = '1128423834057572353'
    replies_list = extract_replies(userId, statusId)

    print('Got {0} replies'.format(len(replies_list)))

    filename = 'replies' + userId + '_' + statusId + '.csv'
    with open('data/' + filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(replies_list)
