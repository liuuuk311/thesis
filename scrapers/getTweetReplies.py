import requests
from bs4 import BeautifulSoup
import json
import logging
import csv
import datetime
import argparse

from textCleaner import clean


def extract_info(soup, user):
    replies = soup.find_all('div', {'class': 'content'})

    res = []

    for reply in replies:
        tweetId = reply.parent['data-tweet-id']
        
        name = reply.find('span', {'class' : 'FullNameGroup'}).get_text().strip()
        user = reply.find('span', {'class' : 'username'}).get_text().strip()

        replyTo = reply.find('div', {'class' : 'ReplyingToContextBelowAuthor'})
        if replyTo is not None: 
            replyTo = replyTo.get_text().strip()

        timestamp = reply.find('span', {'class' : '_timestamp'})['data-time-ms']
        date = datetime.datetime.fromtimestamp(int(timestamp)/1000)  

        text = reply.find('p', {'class' : 'tweet-text'})

        if text is not None: 
            emojis = text.find_all('img', {'class': 'Emoji'})
            text = text.get_text().strip()
            
            emoji_list = []
            for emoji in emojis:
                emoji_list.append(emoji['alt'])
            
            text = text + ' '.join(emoji_list)

        actions = reply.find_all('span', {'class' : 'ProfileTweet-actionCountForPresentation'})
        

        commentCount = 0
        retweetCount = 0
        favouriteCount = 0

        if len(actions) > 0:
            commentCount = actions[0].get_text()
            retweetCount = actions[1].get_text()
            favouriteCount = actions[3].get_text() 
            
        if text is not None:
            res.append([tweetId, name, user, replyTo, date, text, clean(text), commentCount, retweetCount, favouriteCount])


    return res



def extract_replies(username, statusId):

    baseURL = 'https://twitter.com/' + username + '/status/' + statusId
    getNextURL = 'https://twitter.com/i/' + username + '/conversation/' + statusId + '?include_available_features=1&include_entities=1&reset_error_state=false&max_position='

    logging.info('Getting ' + baseURL)

    count = 0
    res = requests.get(baseURL)
    soup = BeautifulSoup(res.text, 'html.parser')

    replies_list = extract_info(soup, username)

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
        replies_list += extract_info(soup, username)

        logging.info('Reply list ' + str(len(replies_list)))

    return replies_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get all replies from a public Tweet.')
    parser.add_argument('-u', '--username', type=str, help='A Twitter username, without @', required=True, metavar='<username>')
    parser.add_argument('-s', '--status-id', type=str, help='The status id of a public Tweet. You can get the status id from the Tweet url', required=True, metavar='<statusId>')
    parser.add_argument('-o', '--output', type=str, help='The output filename. Default replies_<username>_<status_id>.csv')
    parser.add_argument('--header', action='store_true', help='')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename='replies.log', level=logging.INFO)

    if args.verbose:
        print('Getting replies from @{0}'.format(args.username, args.status_id))
        print('Url: https://twitter.com/{0}/status/{1}'.format(args.username, args.status_id))

    replies_list = extract_replies(args.username, args.status_id)

    if args.verbose:
        print('Got {0} replies'.format(len(replies_list)))

    
    filename = 'replies_' + args.username + '_' + args.status_id + '.csv'
    if args.output is not None:
        filename = args.output

    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if args.header:
            writer.writerow(['id', 'name', 'user', 'replyTo', 'date', 'rawText', 'text', 'commentCount', 'retweetCount', 'favouriteCount'])

        writer.writerows(replies_list)

    if args.verbose:
        print('Output saved in {0}'.format(filename))
