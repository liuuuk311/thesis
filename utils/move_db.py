import os
# Database
import psycopg2
from neo4j import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship

from text_utils import get_hashtags, get_mentions, clean

# Get environment variables
GRAPHENEDB_URL = os.environ.get("GRAPHENEDB_BOLT_URL")
GRAPHENEDB_USER = os.environ.get("GRAPHENEDB_BOLT_USER")
GRAPHENEDB_PASS = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

# Get a connection to the Graph Database
driverRemote = GraphDatabase.driver(
    GRAPHENEDB_URL, auth=basic_auth(GRAPHENEDB_USER, GRAPHENEDB_PASS))


LOCAL_URL = os.environ.get("LOCAL_BOLT_URL")
LOCAL_USER = os.environ.get("LOCAL_BOLT_USER")
LOCAL_PASS = os.environ.get("LOCAL_BOLT_PASS")

localGraph = Graph(LOCAL_URL, auth=(LOCAL_USER, LOCAL_PASS))


# Read 
query = """
MATCH (a)-[r:REPLIES]->(b)
WHERE EXISTS(r.polarity) AND a.valid =1
RETURN a, r, b
LIMIT 15
"""
db = driverRemote.session()
query_result = db.run(query)
results = query_result.data()



# Write
for r in results:
    # Create the user who wrote the Tweet in Tweet 
    userNode = Node('User',
                    displayName= r['a']['displayName'],
                    username= r['a']['username'] )
    localGraph.merge(userNode, 'User', 'username')

    # Create the Tweet node
    tweetNode = Node('Tweet',
                        id=r['a']['id'],
                        text=clean(r['a']['text']),
                        date=r['a']['date'],
                        commentCount=r['a']['commentCount'],
                        retweetCount=r['a']['retweetCount'],
                        favouriteCount=r['a']['favouriteCount'])
    localGraph.merge(tweetNode, 'Tweet', 'id')

    # Check if there exists already a relationship between these nodes
    query = """
        MATCH (a:User)-[r:WROTE]->(t:Tweet)
        WHERE a.username = '{}' AND t.id = '{}'
        RETURN r
    """.format(userNode['username'], tweetNode['id'])
    wrote_rel = localGraph.run(query).data()

    if not wrote_rel: # Then create this relationship
        WROTE = Relationship.type("WROTE")
        localGraph.create(WROTE(userNode, tweetNode))

    # Extract all hashtags the Tweet tags
    hashtags = get_hashtags(clean(r['a']['text']))
    for tag in hashtags:
        tagNode = Node('Hashtag', tag=tag)
        localGraph.merge(tagNode, 'Hashtag', 'tag')

         # Check if there exists already a relationship between these nodes
        query = """
            MATCH (t:Tweet)-[r:TAGS]->(h:Hashtag)
            WHERE t.id = '{}' AND h.tag = '{}'
            RETURN r
        """.format(tweetNode['id'], tagNode['tag'])
        tag_rel = localGraph.run(query).data()

        if not tag_rel: # Then create this relationship
            TAGS = Relationship.type("TAGS")
            localGraph.create(TAGS(tweetNode, tagNode))

    # Extract all mentions the Tweet tags
    mentions = get_mentions(clean(r['a']['text']))
    for tag in mentions:
        tagNode = Node('User', username=tag)
        localGraph.merge(tagNode, 'User', 'username')

         # Check if there exists already a relationship between these nodes
        query = """
            MATCH (t:Tweet)-[r:MENTIONS]->(u:User)
            WHERE t.id = '{}' AND u.username = '{}'
            RETURN r
        """.format(tweetNode['id'], tagNode['username'])
        tag_rel = localGraph.run(query).data()

        if not tag_rel: # Then create this relationship
            MENTIONS = Relationship.type("MENTIONS")
            localGraph.create(MENTIONS(tweetNode, tagNode))




    # Create the main Tweet
    mainTweetNode = Node('Tweet',
                    id=r['b']['id'],
                    text=clean(r['b']['text']),
                    date=r['b']['date'])
    localGraph.merge(mainTweetNode, 'Tweet', 'id')

    # Extract all hashtags the Tweet tags
    hashtags = get_hashtags(clean(r['b']['text']))
    for tag in hashtags:
        tagNode = Node('Hashtag', tag=tag)
        localGraph.merge(tagNode, 'Hashtag', 'tag')

         # Check if there exists already a relationship between these nodes
        query = """
            MATCH (t:Tweet)-[r:TAGS]->(h:Hashtag)
            WHERE t.id = '{}' AND h.tag = '{}'
            RETURN r
        """.format(mainTweetNode['id'], tagNode['tag'])
        tag_rel = localGraph.run(query).data()

        if not tag_rel: # Then create this relationship
            TAGS = Relationship.type("TAGS")
            localGraph.create(TAGS(mainTweetNode, tagNode))

    # Extract all mentions the Tweet tags
    mentions = get_mentions(clean(r['b']['text']))
    for tag in mentions:
        tagNode = Node('User', username=tag)
        localGraph.merge(tagNode, 'User', 'username')

         # Check if there exists already a relationship between these nodes
        query = """
            MATCH (t:Tweet)-[r:MENTIONS]->(u:User)
            WHERE t.id = '{}' AND u.username = '{}'
            RETURN r
        """.format(mainTweetNode['id'], tagNode['username'])
        tag_rel = localGraph.run(query).data()

        if not tag_rel: # Then create this relationship
            MENTIONS = Relationship.type("MENTIONS")
            localGraph.create(MENTIONS(mainTweetNode, tagNode))

    query = """
        MATCH (r:Tweet)-[p:REPLIES]->(t:Tweet)
        WHERE r.id = '{}'
        RETURN p
    """.format(tweetNode['id'])
    polarity_rel = localGraph.run(query).data()

    
    if not polarity_rel:
        REL = Relationship.type("REPLIES")
        localGraph.create(REL(tweetNode, mainTweetNode, values=[]))

    query = """
        MATCH (r:Tweet)-[p:REPLIES]->(t:Tweet)
        WHERE r.id = '{}'
        SET p.values = p.values + '{}'
    """.format(tweetNode['id'], r['r']['polarity'])
    localGraph.run(query)