import os
# Database
import psycopg2
from neo4j import GraphDatabase, basic_auth
from py2neo import Graph, Node, Relationship


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
"""
db = driverRemote.session()
query_result = db.run(query)
results = query_result.data()

# Write
for r in results:
    userNode = Node('User',
                    displayName= r['a']['displayName'],
                    username= r['a']['username'] )
    localGraph.merge(userNode, 'User', 'username')

    replyNode = Node('Reply',
                        id=r['a']['id'],
                        text=r['a']['text'],
                        date=r['a']['date'],
                        commentCount=r['a']['commentCount'],
                        retweetCount=r['a']['retweetCount'],
                        favouriteCount=r['a']['favouriteCount'])

    WROTE = Relationship.type("WROTE")
    localGraph.create(WROTE(userNode, replyNode))

    tweetNode = Node('Tweet',
                    id=r['b']['id'],
                    text=r['b']['text'],
                    date=r['b']['date'])
    localGraph.merge(tweetNode, 'Tweet', 'id')

    REL = Relationship.type(r['r']['polarity'])
    localGraph.create(REL(replyNode, tweetNode))