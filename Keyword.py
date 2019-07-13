# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import tweepy
from ibm_watson import ToneAnalyzerV3
import json
app = Flask(__name__)
CORS(app)


#search_words = "india vs pakistan"
#date_since = "2018-11-16"

class DataStore:
    searchedTweets = [ ]
    api = None

data = DataStore()

@app.route('/')
def init():
    return jsonify(msg="Welcome")

@app.route('/login')
def login():
    if 'ckey' and 'csecret' and 'atoken' and 'asecret' in request.args:
        consKey = request.args['ckey']
        consSec = request.args['csecret']
        accessTok = request.args['atoken']
        accessSec = request.args['asecret']
        auth = tweepy.OAuthHandler(consKey, consSec)
        auth.set_access_token(accessTok, accessSec)
        data.api = tweepy.API(auth)
        userProfile = data.api.me()
        return jsonify(msg="Logged in as "+userProfile.screen_name)
    else:
        return jsonify(msg="Error while logging in")


@app.route('/fetchTweets')
def fetchtweets():
    if 'keyword' in request.args:
        array = []
        key = request.args['keyword']
        data.searchedTweets = tweepy.Cursor(data.api.search,q=key+' -filter:retweets',lang="en",since="2018-01-01",show_user=True).items(20)
        for tweet in data.searchedTweets:
            json = {}
            text = tweet.text.encode('utf-8')
            user = tweet.user.screen_name.encode('utf-8')
            loc = tweet.user.location.encode('utf-8')
            json['username'] = str(user)
            json['tweet'] = str(text)
            json['location'] = str(loc)
            array.append(json)
        return jsonify(response=array)

@app.route('/analyze')
def analyze():
    if 'text' in request.args:
        tweets = request.args['text']
        tone_analyzer = ToneAnalyzerV3(
            version='2017-09-21',
            iam_apikey='XyvXKBvFq1Z_e1DFiGWl-CDjr7C7YJaAYiwzrRvVnhF_',
            url='https://gateway-lon.watsonplatform.net/tone-analyzer/api'
        )
        tone_analysis = tone_analyzer.tone(
            {'text': tweets},
            content_type='application/json'
        ).get_result()
    return jsonify(moods=tone_analysis)

if __name__ == '__main__':
    app.run()