from flask import Flask, request, jsonify, url_for
import os
import json
import requests
import tweepy

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def twitter_auth():
    try:
        consumer_key = '5gkw8QMwVpUL6hhKAFNSmCJir'
        consumer_secret = '9f0zGW1pebrmAXyMeTroK8W7z0rxlQz41ADanVx1rxFdYk7Qr3'
        access_token = '157449530-vBGOFXkgPrbN1qBwIO1MVotnrjS6daSrQpljePSw'
        access_token_secret = 'g1Kk90vFyktBPAwqE9EIwjLhIFOEnOGQPjDfWi4AKxsaU'

    except:
        return "missing keys"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth

def get_twitter_client(tw_auth):
    auth = tw_auth
    client = tweepy.API(auth, wait_on_rate_limit=True)
    return client
    
