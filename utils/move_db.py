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
LIMIT 5
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
    
    localGraph.merge(replyNode, 'Reply', 'id')
    query = """
        MATCH (a:User)-[r:WROTE]->(t:Reply)
        WHERE a.username = '{}' AND t.id = '{}'
        RETURN r
    """.format(userNode['username'], replyNode['id'])

    wrote_rel = localGraph.run(query).data()

    if not wrote_rel:
        WROTE = Relationship.type("WROTE")
        localGraph.create(WROTE(userNode, replyNode))

    tweetNode = Node('Tweet',
                    id=r['b']['id'],
                    text=r['b']['text'],
                    date=r['b']['date'])
    localGraph.merge(tweetNode, 'Tweet', 'id')


    query = """
        MATCH (r:Reply)-[p:POLARITY]->(t:Tweet)
        WHERE r.id = '{}'
        RETURN p
    """.format(replyNode['id'])
    polarity_rel = localGraph.run(query).data()

    
    if not polarity_rel:
        REL = Relationship.type("POLARITY")
        localGraph.create(REL(replyNode, tweetNode, values=[]))

    query = """
        MATCH (r:Reply)-[p:POLARITY]->(t:Tweet)
        WHERE r.id = '{}'
        SET p.values = p.values + '{}'
    """.format(replyNode['id'], r['r']['polarity'])
    localGraph.run(query)