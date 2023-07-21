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
import pytz

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

TWITTER_NOTE_SPACING=int(os.getenv('TWITTER_NOTE_SPACING'))
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
        "INSERT INTO cronjob_logs (job_description, executed_at, error_logs) VALUES (%s, %s, %s)",
        ("Executing publishQueuedTweets.py", datetime.datetime.now(tz), json.dumps([]))
    )

    # Remember the ID of the log entry
    log_id = cursor.lastrowid
    conn.commit()

    # Select all queued tweets, ordered by note_id and id
    cursor.execute("SELECT id, tweet, note_id, media_id FROM queued_tweets ORDER BY note_id, id")
    queued_tweets = cursor.fetchall()

    # initialize previous_tweet_id to None and previous_note_id to None
    previous_tweet_id = None
    previous_note_id = None

    rate_limit_hit = False
    error_logs = []

    i = 0
    note_id = 0
    for tweet in queued_tweets:
        i += 1
        tweet_id, tweet_text, note_id, media_id = tweet

        if media_id is not None:
            payload = {"text": tweet_text, "media": {"media_ids": [media_id]}}
        else:
            payload = {"text": tweet_text}

        # check if any tweet has been posted in the last TWITTER_NOTE_SPACING  hours for the same note_id
        cursor.execute(
            "SELECT posted_at FROM tweets WHERE note_id = %s AND posted_at > %s ORDER BY posted_at DESC LIMIT 1",
            (note_id, datetime.datetime.now(tz) - datetime.timedelta(hours=TWITTER_NOTE_SPACING))
        )
        last_tweet = cursor.fetchone()

        if last_tweet is not None:  # If a tweet from the same note_id was posted in the last TWITTER_NOTE_SPACING hours
            # Add the tweet to the 'spaced_tweets' table with a scheduled_at value 72 hours after the last tweet
            cursor.execute(
                "INSERT INTO spaced_tweets (tweet, scheduled_at, note_id, media_id) VALUES (%s, %s, %s, %s)",
                (tweet_text, last_tweet[0] + datetime.timedelta(hours=TWITTER_NOTE_SPACING), note_id, media_id)
            )
            conn.commit()

            # Delete the tweet from the 'queued_tweets' table
            cursor.execute("DELETE FROM queued_tweets WHERE id = %s", (tweet_id,))
            conn.commit()

            print(f"Tweet added to spaced queue: {tweet_text}")
            continue  # Skip to the next tweet

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
            error_message = f"Rate limit exceeded. Queued tweets for {note_id} have not been posted"
            print(error_message)
            rate_limit_hit = True
            error_logs.append(error_message)
            break

        if response.status_code != 201:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

        json_response = response.json()

        if 'data' in json_response:
            # get the id of the tweet
            tw_id = json_response['data']['id']

            # Insert into the 'tweets' table
            cursor.execute(
                "INSERT INTO tweets (tweet, tweet_id, note_id, media_id) VALUES (%s, %s, %s, %s)",
                (tweet_text, tw_id, note_id, media_id)
            )
            conn.commit()

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
            ("publishQueuedTweets.py", json.dumps(error_logs), log_id)
        )
    else:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s WHERE id = %s",
            ("publishQueuedTweets.py", log_id)
        )
        published_at = datetime.datetime.now(tz)
        update_cmd = ("UPDATE notes SET is_published = 1, published_at = %s WHERE id = %s")
        cursor.execute(update_cmd, (published_at, note_id,))
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

