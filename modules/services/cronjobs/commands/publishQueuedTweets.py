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
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
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

def publish_queued_tweets():
    # Create a new Cursor
    cursor = conn.cursor()

    # Log the start of the job
    cursor.execute(
        "INSERT INTO cronjob_logs (job_description, executed_at, error_logs) VALUES (%s, NOW(), %s)",
        ("Publishing queued tweets", json.dumps([]))
    )

    # Remember the ID of the log entry
    log_id = cursor.lastrowid
    conn.commit()

    # Select all queued tweets, ordered by note_id and id
    cursor.execute("SELECT id, tweet, note_id FROM queued_tweets ORDER BY note_id, id")
    queued_tweets = cursor.fetchall()

    # initialize previous_tweet_id to None and previous_note_id to None
    previous_tweet_id = None
    previous_note_id = None

    rate_limit_hit = False
    error_logs = []

    for tweet in queued_tweets:
        tweet_id, tweet_text, note_id = tweet

        payload = {"text": tweet_text}

        # add the previous tweet id to the payload if it's from the same note
        if previous_tweet_id is not None and note_id == previous_note_id:
            payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}

        # If it's a new note_id, look for a tweet in the 'tweets' table with the same note_id
        elif note_id != previous_note_id:
            cursor.execute("SELECT tweet_id FROM tweets WHERE note_id = %s ORDER BY posted_at DESC LIMIT 1", (note_id,))
            result = cursor.fetchone()
            if result is not None:  # If a tweet from the same note_id exists
                payload["reply"] = {"in_reply_to_tweet_id": result[0]}  # reply to this tweet

        time.sleep(1)
        oauth = get_oauth_session()

        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code == 429:  # Rate limit exceeded
            error_message = f"Rate limit exceeded. Tweet with id {tweet_id} has not been posted."
            print(error_message)
            rate_limit_hit = True
            error_logs.append(error_message)
            continue  # Skip to the next tweet

        if response.status_code != 201:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

        json_response = response.json()

        if 'data' in json_response:
            # get the id of the tweet
            tw_id = json_response['data']['id']

            # update previous_tweet_id
            previous_tweet_id = tw_id

            # update previous_note_id
            previous_note_id = note_id

            # If the tweet is successfully posted, delete it from the queue
            cursor.execute("DELETE FROM queued_tweets WHERE id = %s", (tweet_id,))
            conn.commit()

            print(f"Tweeted and removed from queue: {tweet_text}")

    # Update the job log entry with the final status
    if rate_limit_hit:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("Job finished with some tweets not posted due to rate limit.", json.dumps(error_logs), log_id)
        )
    else:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s WHERE id = %s",
            ("Job finished successfully with all tweets posted.", log_id)
        )
    conn.commit()


def get_oauth_session():

    oauth = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
    )

    response = oauth.post("https://api.twitter.com/2/tweets")
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

    return oauth


if __name__ == '__main__':
    publish_queued_tweets()

