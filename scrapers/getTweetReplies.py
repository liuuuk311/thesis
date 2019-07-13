import requests
from bs4 import BeautifulSoup
import json
import logging
import csv
import datetime
import argparse

from textCleaner import clean

import os
from py2neo import Graph, Node, Relationship


# Get environment variables
GRAPHENEDB_URL = os.environ.get("GRAPHENEDB_BOLT_URL")
GRAPHENEDB_USER = os.environ.get("GRAPHENEDB_BOLT_USER")
GRAPHENEDB_PASS = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

graph = Graph(GRAPHENEDB_URL, auth=(
    GRAPHENEDB_USER, GRAPHENEDB_PASS), secure=True)


def translate_month(date):
    return date.replace('gen', 'jan').replace('mag', 'may').replace('giu', 'jun').replace('lug', 'jul').replace('ago', 'aug').replace('set', 'sep').replace('ott', 'oct').replace('dic', 'dec')


def extract_parent_tweet(soup):
    mainTweet = soup.find('div', {'class': 'permalink-tweet-container'})
    if mainTweet:
        mainTweet = mainTweet.find('div', {'class': 'tweet'})
        parentId = mainTweet['data-tweet-id']
        rawParentText = mainTweet.find(
            'p', {'class': 'tweet-text'}).get_text().strip().replace('\n', '')
        parentText = clean(rawParentText)

        date = mainTweet.find('span', {'class': 'metadata'})
        date = date.span.get_text()
        date = datetime.datetime.strptime(
            translate_month(date), '%H:%M - %d %b %Y')
        mainTweet = Node('Tweet',
                         id=parentId,
                         text=parentText,
                         date=str(date.strftime('%d/%m/%Y-%H:%M:%S')))
        graph.merge(mainTweet, 'Tweet', 'id')

    return mainTweet
    # return [parentId, rawParentText, parentText]


def extract_info(soup, mainTweet, username):

    replies = soup.find_all('div', {'class': 'content'})

    res = []

    for reply in replies:
        tweetId = reply.parent['data-tweet-id']

        name = reply.find(
            'span', {'class': 'FullNameGroup'}).get_text().strip()
        user = reply.find('span', {'class': 'username'}).get_text().strip()

        replyTo = reply.find('div', {'class': 'ReplyingToContextBelowAuthor'})
        if replyTo is not None:
            replyTo = replyTo.get_text().strip()

        timestamp = reply.find('span', {'class': '_timestamp'})['data-time-ms']
        date = datetime.datetime.fromtimestamp(int(timestamp)/1000)

        text = reply.find('p', {'class': 'tweet-text'})

        if text is not None:
            emojis = text.find_all('img', {'class': 'Emoji'})
            text = text.get_text().strip().replace('\n', ' ')

            emoji_list = []
            for emoji in emojis:
                emoji_list.append(emoji['alt'])

            text = text + ' '.join(emoji_list)

        actions = reply.find_all(
            'span', {'class': 'ProfileTweet-actionCountForPresentation'})

        commentCount = 0
        retweetCount = 0
        favouriteCount = 0

        if len(actions) > 0:
            commentCount = actions[0].get_text()
            retweetCount = actions[1].get_text()
            favouriteCount = actions[3].get_text()

        if text is not None and replyTo == 'In risposta a @' + username and len(clean(text)) > 2:

            userNode = Node('User',
                            id=user,
                            name=name
                            )
            graph.merge(userNode, 'User', 'id')
            replyNode = Node('Tweet',
                             id=tweetId,
                             text=clean(text),
                             date=str(date.strftime('%d/%m/%Y-%H:%M:%S')),
                             commentCount=commentCount,
                             retweetCount=retweetCount,
                             favouriteCount=favouriteCount
                             )

            graph.merge(replyNode, 'Tweet', 'id')

            WROTE = Relationship.type("WROTE")
            graph.create(WROTE(userNode, replyNode))

            REPLIES = Relationship.type("REPLIES")
            graph.create(REPLIES(replyNode, mainTweet))


def extract_replies(username, statusId):

    baseURL = 'https://twitter.com/' + username + '/status/' + statusId
    getNextURL = 'https://twitter.com/i/' + username + '/conversation/' + statusId + \
        '?include_available_features=1&include_entities=1&reset_error_state=false&max_position='

    logging.info('Getting ' + baseURL)

    count = 0
    res = requests.get(baseURL)
    soup = BeautifulSoup(res.text, 'html.parser')

    main_tweet = extract_parent_tweet(soup)
    extract_info(soup, main_tweet, username)

    div = soup.find('div', {'class': 'stream-container'})
    min_pos = div['data-min-position']

    while min_pos is not None:
        logging.info('Looking for next data. Min position ' + str(min_pos))
        logging.info('Getting ' + getNextURL + min_pos)
        res = requests.get(getNextURL + min_pos)
        res = json.loads(res.text)
        min_pos = res['min_position']

        soup = BeautifulSoup(res['items_html'], 'html.parser')
        extract_info(soup, main_tweet, username)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Get all replies from a public Tweet.')
    parser.add_argument('-u', '--username', type=str,
                        help='A Twitter username, without @', required=True, metavar='<username>')
    parser.add_argument('-s', '--status-id', type=str,
                        help='The status id of a public Tweet. You can get the status id from the Tweet url', required=True, metavar='<statusId>')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s: %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S', filename='replies.log', level=logging.INFO)

    if args.verbose:
        print('Getting replies from @{0}'.format(
            args.username, args.status_id))
        print(
            'Url: https://twitter.com/{0}/status/{1}'.format(args.username, args.status_id))

    extract_replies(args.username, args.status_id)

    if args.verbose:
        pass

    if args.verbose:
        print('Output saved in {0}'.format(filename))
