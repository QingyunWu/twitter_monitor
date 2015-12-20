from flask import Flask
from flask import render_template
from pymongo import MongoClient
import pymongo
import json
from bson import json_util
from bson.json_util import dumps
from flask import request, redirect
import sys
import tweepy
#, 'created_at': True, '_id': False
app = Flask(__name__)

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'twitterdata'
COLLECTION_NAME = 'log'
FIELDS1 = {'text': True, '_id': False}
FIELDS2 = {'user.followers_count': True, '_id': False, 'user.name':True}
FIELDS3 = {'coordinates.coordinates': True, '_id': False}

access_key = "72059133-YuX6QTNA2jMAu6Xb2XywmZjvVRzDRDrXpjnSTnt8i"
access_secret = "eRFfZdASnzpMZKRTuZah7yv4cvZyJPIQ5yx370TAt5ekV"
consumer_key = "Ecc0HBcByxtZU0xRVXpiM6k9W"
consumer_secret = "ihdwCMtghcaoRgaeK37qtsos0FoWsqBiAjd558rgySP2LYMnV5"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        self.db = pymongo.MongoClient().twitterdata
  
    def on_data(self, tweet):
        self.db.log.insert(json.loads(tweet))
        print(json.loads(tweet))


    def on_error(self, status_code):
        print >> sys.stderr, 'Error *** ', status_code
        return True 


    def on_timeout(self):
        print >> sys.stderr, 'Timeout happened. Check for network connection and restart the program.'
        return True 

setTerms = ['chelsea','arsenal','liverpool','curry'] #add the list of terms, upto 16 that you want to look for.
sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/log")
def projects():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS1)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

@app.route("/user")
def user():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS2)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

@app.route("/geo")
def geo():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS3)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

@app.route('/signup', methods = ['POST'])
def signup():
    if request.form.get('Search',None) == 'Search':
        email = request.form.get('email')
        setTerms = [email] #add the list of terms, upto 16 that you want to look for.
        print("The email address is '" + setTerms[0] + "'")
        sapi.filter(None,setTerms, async=True)
    elif request.form.get('Rest',None) == 'rest':
        sapi.disconnect()
        connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
        collection = connection[DBS_NAME][COLLECTION_NAME]
        collection.drop()
        print "stream disconnect"
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
