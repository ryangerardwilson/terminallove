import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
import subprocess
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt
import time
from requests_oauthlib import OAuth1Session
import json


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
  
conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

def fn_list_tweets():

    cursor = conn.cursor()
    print('List tweets')

def fn_list_scheduled_tweets():
     
     cursor = conn.cursor()
     print('List scheduled tweets')

def fn_tweet_out_note(called_function_arguments_dict):

    cursor = conn.cursor()

    print('tweet')

    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    note_id = int(called_function_arguments_dict.get('id', 0))
    TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET')
    TWITTER_ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

    if note_id != 0:

        select_cmd = ("SELECT note FROM notes WHERE id = %s")
        cursor.execute(select_cmd, (note_id,))
        tweet_text = cursor.fetchone()

        if tweet_text is not None:
            tweet_text = tweet_text[0]
        else:
            print(colored("You can't tweet an empty note", 'red'))
            return

        # Check if the tweet already exists in the tweets table
        check_cmd = ("SELECT tweet FROM tweets WHERE tweet = %s")
        cursor.execute(check_cmd, (tweet_text,))
        if cursor.fetchone() is not None:
            print(colored("This tweet already has been posted", 'red'))
            return

        payload = {"text": tweet_text}

        oauth = OAuth1Session(
            TWITTER_CONSUMER_KEY,
            TWITTER_CONSUMER_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET,
        )

        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code != 201:

            # Load existing tokens from file, if available
            tokens_file = f"{parent_dir}/files/tokens/rgw-tokens.json"
            try:
                with open(tokens_file, 'r') as f:
                    tokens = json.load(f)
                access_token = tokens['access_token']
                access_token_secret = tokens['access_token_secret']
            except FileNotFoundError:
                # Get new tokens and save them to file
                request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
                oauth = OAuth1Session(TWITTER_CONSUMER_KEY, client_secret=TWITTER_CONSUMER_SECRET)

                try:
                    fetch_response = oauth.fetch_request_token(request_token_url)
                except ValueError:
                    print("There may have been an issue with the consumer_key or consumer_secret you entered.")

                resource_owner_key = fetch_response.get("oauth_token")
                resource_owner_secret = fetch_response.get("oauth_token_secret")
                print("Got OAuth token: %s" % resource_owner_key)

                base_authorization_url = "https://api.twitter.com/oauth/authorize"
                authorization_url = oauth.authorization_url(base_authorization_url)
                print("Please go here and authorize: %s" % authorization_url)
                verifier = input("Paste the PIN here: ")

                access_token_url = "https://api.twitter.com/oauth/access_token"
                oauth = OAuth1Session(
                    TWITTER_CONSUMER_KEY,
                    client_secret=TWITTER_CONSUMER_SECRET,
                    resource_owner_key=resource_owner_key,
                    resource_owner_secret=resource_owner_secret,
                    verifier=verifier,
                )
                oauth_tokens = oauth.fetch_access_token(access_token_url)

                access_token = oauth_tokens["oauth_token"]
                access_token_secret = oauth_tokens["oauth_token_secret"]

                # Save tokens to file
                with open(tokens_file, 'w') as f:
                    json.dump({'access_token': access_token, 'access_token_secret': access_token_secret}, f)

            # Use the tokens for the API call
            oauth = OAuth1Session(
                TWITTER_CONSUMER_KEY,
                client_secret=TWITTER_CONSUMER_SECRET,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret,
            )

            response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

            if response.status_code != 201:
                raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

        print("Response code: {}".format(response.status_code))

        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        
        if 'data' in json_response:
            # get the id of the tweet
            tweet_id = json_response['data']['id']

            # get current time
            posted_at = datetime.datetime.now()

            # prepare insert command
            insert_cmd = ("INSERT INTO tweets (tweet, tweet_id, posted_at) VALUES (%s, %s, %s)")
            
            # insert the tweet into the database
            cursor.execute(insert_cmd, (tweet_text, tweet_id, posted_at))
            conn.commit()  # don't forget to commit the transaction






def fn_schedule_tweet(called_function_arguments_dict):

    cursor = conn.cursor()
    print('schedule tweet')
    
    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_edit_tweet(called_function_arguments_dict):

    cursor = conn.cursor()
    print('edit tweet')
    
    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_delete_tweets_by_ids(called_function_arguments_dict):

    cursor = conn.cursor()
    print('delete tweets by ids')

    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

