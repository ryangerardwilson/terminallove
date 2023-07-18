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

def fn_list_tweets(called_function_arguments_dict):

    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 10))

    query = "SELECT * FROM tweets ORDER BY posted_at DESC LIMIT %s"
    cursor.execute(query, (limit,))

    # Fetch all columns
    columns = [col[0] for col in cursor.description]

    # Fetch all rows
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if not result:
        print("No result found")
        return

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)

    if 'value' in df.columns:
        df['value'] = df['value'].astype(int)

    # Truncate note column to 300 characters and add "...." if it exceeds that limit
    if 'tweet' in df.columns:
        df['tweet'] = df['tweet'].apply(lambda x: (x[:300] + '....') if len(x) > 300 else x)

    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"TWEETS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_list_scheduled_tweets():
     
     cursor = conn.cursor()
     print('List scheduled tweets')

def fn_tweet_out_note(called_function_arguments_dict):

    cursor = conn.cursor()

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

        oauth = get_oauth_session()
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

        if response.status_code != 201:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

        print("Response code: {}".format(response.status_code))

        json_response = response.json()
        
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

            # Now let's fetch the tweet we just inserted and print it
            fetch_tweet_cmd = ("SELECT * FROM tweets WHERE tweet_id = %s")
            cursor.execute(fetch_tweet_cmd, (tweet_id,))

            # Fetch all columns
            columns = [col[0] for col in cursor.description]

            # Fetch all rows
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            if not result:
                print("No result found")
                return

            # Convert the result to DataFrame
            pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
            df = pd.DataFrame(result)

            # Truncate tweet column to 300 characters and add "...." if it exceeds that limit
            df['tweet'] = df['tweet'].apply(lambda x: (x[:300] + '....') if len(x) > 300 else x)

            # Construct and print the heading
            heading = f"NEWLY POSTED TWEET DETAILS"
            print()
            print(colored(heading, 'cyan'))
            print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

            cursor.close()

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
    ids_to_delete = called_function_arguments_dict.get('ids').split('_')
    deleted_ids = []  # to store the successfully deleted tweet ids

    oauth = get_oauth_session()

    for table_id in ids_to_delete:
        # Fetch the corresponding tweet_id from the database
        select_cmd = "SELECT tweet_id FROM tweets WHERE id = %s"
        cursor.execute(select_cmd, (table_id,))
        result = cursor.fetchone()

        if result is None:
            print(colored(f"No tweet found with ID {table_id}", 'red'))
            continue

        tweet_id = result[0]

        # Delete the tweet on Twitter
        url = f"https://api.twitter.com/2/tweets/:{tweet_id}"

        response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(tweet_id))

        # Check for a successful response
        if response.status_code == 200:
            # If the deletion was successful on Twitter, delete the record from the tweets table
            sql = "DELETE FROM tweets WHERE id = %s"
            cursor.execute(sql, (table_id,))
            deleted_ids.append(table_id)  # adding the id to the deleted_ids list
        else:
            print(colored(f"FAILED TO DELETE TWEET WITH ID {table_id}", 'red'))
            print(response)

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"TWEETS WITH IDS {deleted_ids} SUCCESSFULLY DELETED", 'cyan'))

def get_oauth_session():
    TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET')
    TWITTER_ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

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

