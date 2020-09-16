from flask import Flask, request, jsonify, url_for
import os
import json
import requests
import tweepy

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def twitter_auth():
    try:
        consumer_key = 'RpFMUcMoxysBdxEKposxkxisa'
        consumer_secret = 'pFlnrS3MQ060s6SMkW4f7NZOqXhsT9ogXtbCYsYffcuCD7zo3G'
        access_token = '157449530-g9V1HOm05CItASP58Ubjt5dJ5rkUQSvZZj6PFkvJ'
        access_token_secret = 'jU19ySczJz6ywm0h5KkCiaNjUDuDDUtOMZhRhXUOuqJQJ'

    except:
        return "missing keys"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth

def get_twitter_client(tw_auth):
    auth = tw_auth
    client = tweepy.API(auth, wait_on_rate_limit=True)
    return client
    
    # if __name__ == '__main__':
    #     user = 'JuanGcardinale'
    #     client = get_twitter_client()
    #     for tweet in tweepy.Cursor(client.home_timeline, screen_name=user).items(10):
    #         print(tweet.text) 