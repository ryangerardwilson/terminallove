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
import requests
import pytz
from pytz import timezone
import base64
from google.cloud import storage


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

OPEN_AI_API_KEY=os.getenv('OPEN_AI_API_KEY')

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

NOTE_IMAGE_STORAGE_BUCKET_NAME=os.getenv('NOTE_IMAGE_STORAGE_BUCKET_NAME')
GOOGLE_SERVICE_ACCOUNT_KEY=os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
path_to_service_account_file=os.path.join(parent_dir,'files/tokens/',GOOGLE_SERVICE_ACCOUNT_KEY)

TWITTER_AUTHENTICATION_KEY=os.getenv('TWITTER_AUTHENTICATION_KEY')
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

def fn_list_twitter_module_functions(called_function_arguments_dict):

    functions = [
        {
            "function": "list_tweets",
            "description": "Lists the user's tweets",
        },
        {
            "function": "list_rate_limits",
            "description": "Lists Twitter rate limits",
        },
       
    ]
    # Convert the passwords to a list of lists
    rows = [
        [index + 1, entry["function"], entry["description"]]
        for index, entry in enumerate(functions)
    ]

    # Column names
    column_names = ["", "function", "description"]

    # Print the passwords in tabular form
    print()
    print(colored('TWITTER MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_list_twitter_rate_limits(called_function_arguments_dict):
    oauth = get_oauth_session() # this function should return an OAuth1Session or OAuth2Session instance
    
    url = "https://api.twitter.com/2/tweets/"

    paragraph = ''
    payload = {"text": paragraph}
    response = oauth.post(url, json=payload)

    print(colored(f"https://api.twitter.com/2/tweets/ endpoint response status code for blank tweet: {response.status_code}",'cyan'))

    rate_limit_limit = response.headers.get('x-rate-limit-limit')
    rate_limit_remaining = response.headers.get('x-rate-limit-remaining')
    rate_limit_reset = response.headers.get('x-rate-limit-reset')

    rate_limit_reset_date = datetime.datetime.utcfromtimestamp(int(rate_limit_reset))
    rate_limit_reset_date = rate_limit_reset_date.replace(tzinfo=pytz.utc).astimezone(tz)

    print(colored(f"rate limit ceiling: {rate_limit_limit}",'cyan'))
    print(colored(f"rate limit remaining: {rate_limit_remaining}",'cyan'))
    print(colored(f"rate limit reset: {rate_limit_reset_date}",'cyan'))


def fn_list_tweets(called_function_arguments_dict):

    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 20))

    if limit < 20:
        limit = 20

    query = "SELECT * FROM tweets ORDER BY id DESC LIMIT %s"
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
        df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Convert posted_at to IST
    if 'posted_at' in df.columns:
        ist = pytz.timezone('Asia/Kolkata')
        df['posted_at'] = df['posted_at'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(ist))


    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"TWEETS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


