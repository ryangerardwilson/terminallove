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

LINKEDIN_CLIENT_ID=os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET=os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URL=os.getenv('LINKEDIN_REDIRECT_URL')

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

def fn_list_linkedin_module_functions():

    functions = [
            {
                "function": "list_linkedin_posts",
                "description": "Lists the user's LinkedIn posts",
            },
            {
                "function": "list_rate_limits",
                "description": "Lists LinkedIn rate limits",
            },

            {
                "function": "list_queued_tweets",
                "description": "Lists the user's queued LinkedIn posts",
            },
            {
                "function": "list_spaced_tweets",
                "description": "Lists the user's scheduled LinkedIn posts, also known as spaced LinkedIn posts",
            },
            {
                "function": "linkedin_post_out_note",
                "description": "Posts to LinkedIn the note prepared by the user by its ids",
            },
            {
                "function": "schedule_linkedin_post",
                "description": "Schedules the LinkedIn posting of the note prepared by the user to a later date",
            },
            {
                "function": "edit_linkedin_post",
                "description": "Edits the user's LinkedIn post",
            },
            {
                "function": "delete_linkedin_posts_by_ids",
                "description": "Deletes LinkedIn posts by their ids",
            },
            {
                "function": "delete_linkedin_posts_by_note_ids",
                "description": "Deletes LinkedIn posts by their note ids",
            },
            {
                "function": "delete_queued_linkedin_posts_by_ids",
                "description": "Deletes queued LinkedIn posts by their ids",
            },
            {
                "function": "delete_queued_linkedin_posts_by_note_ids",
                "description": "Deletes queued LinkedIn posts by their note ids",
            },
            {
                "function": "delete_spaced_linkedin_posts_by_ids",
                "description": "Deletes spaced/ scheduled LinkedIn posts by their ids",
            },        
            {
                "function": "delets_spaced_linkedin_posts_by_their_note_ids",
                "description": "Deletes spaced/ scheduled LinkedIn posts by their note ids",
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
    print(colored('LINKEDIN MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_list_rate_limits():
    access_token, linkedin_id = get_active_access_token_and_linkedin_id() # this function should return an OAuth1Session or OAuth2Session instance
   
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    data = {
        'author': f"urn:li:person:{linkedin_id}",  # replace with your LinkedIn ID
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': ''
                },
                'shareMediaCategory': 'NONE'
            }
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
    }

    response = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, data=json.dumps(data))


    if response.status_code != 429:
        print(colored("Rate limit is not exceeded yet", 'cyan'))

    return












 
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    data = {
        'author': f"urn:li:person:{linkedin_id}",  # replace with your LinkedIn ID
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {
                    'text': 'Hello World! This is my first Share on LinkedIn!'
                },
                'shareMediaCategory': 'NONE'
            }
        },
        'visibility': {
            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
        }
    }

    response = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, data=json.dumps(data)) 
    post_id = response.headers.get('X-RestLi-Id') 
    print(response) 
    print(response.content) 
    print(post_id) 


    return


    url = "https://api.twitter.com/2/tweets/"

    paragraph = ''
    payload = {"text": paragraph}
    response = oauth.post(url, json=payload)

    print(colored(f"https://api.twitter.com/2/tweets/ endpoint response status code for blank tweet: {response.status_code}",'cyan'))

    rate_limit_limit = response.headers.get('X-RateLimit-Limit')
    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
    rate_limit_reset = response.headers.get('X-RateLimit-Reset')

    print(colored(f"rate limit ceiling: {rate_limit_limit}",'cyan'))
    print(colored(f"rate limit remaining: {rate_limit_remaining}",'cyan'))
    print(colored(f"rate limit reset: {rate_limit_reset}",'cyan'))


def fn_list_linkedin_posts(called_function_arguments_dict):

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

def fn_list_queued_linkedin_posts(called_function_arguments_dict):

    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 20))

    if limit < 20:
        limit = 20

    query = "SELECT * FROM queued_tweets ORDER BY id DESC LIMIT %s"
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

    # Truncate note column to 30 characters and add "...." if it exceeds that limit
    if 'tweet' in df.columns:
        df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Convert executed_at to IST
    if 'tweet_failed_at' in df.columns:
        ist = pytz.timezone('Asia/Kolkata')
        df['tweet_failed_at'] = df['tweet_failed_at'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(ist))


    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"QUEUED TWEETS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

def fn_list_spaced_linkedin_posts(called_function_arguments_dict):
    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 20))

    if limit < 20:
        limit = 20

    query = "SELECT * FROM spaced_tweets ORDER BY id DESC LIMIT %s"
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

    # Truncate note column to 30 characters and add "...." if it exceeds that limit
    if 'tweet' in df.columns:
        df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"SPACED TWEETS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

def fn_schedule_linkedin_post(called_function_arguments_dict):

    cursor = conn.cursor()
    print('schedule tweet')
    
    # Set default values
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_edit_linkedin_post(called_function_arguments_dict):

    cursor = conn.cursor()
    print('edit tweet')
    
    # Set default values
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_delete_linkedin_posts_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    ids_to_delete = called_function_arguments_dict.get('ids').split('_')
    deleted_ids = []  # to store the successfully deleted tweet ids

    oauth = get_oauth_session()

    for table_id in ids_to_delete:
        # Fetch the corresponding tweet_id and note_id from the database
        select_cmd = "SELECT tweet_id, note_id FROM tweets WHERE id = %s"
        cursor.execute(select_cmd, (table_id,))
        result = cursor.fetchone()
    
        if result is None:
            print(colored(f"No tweet found with ID {table_id}", 'red'))
            continue

        tweet_id, note_id = result

        # Check if note_id is not null and there is a corresponding row in the notes table
        if note_id is not None:
            cursor.execute("SELECT 1 FROM notes WHERE id = %s", (note_id,))
            note_exists = cursor.fetchone() is not None
            if not note_exists:
                print(colored(f"No corresponding note found for tweet with ID {table_id}", 'red'))
                continue
        else:
            print(colored(f"No corresponding note ID found for tweet with ID {table_id}", 'red'))
            continue

        # Delete the tweet on Twitter
        url = f"https://api.twitter.com/2/tweets/:{tweet_id}"
        time.sleep(1)
        response = oauth.delete("https://api.twitter.com/2/tweets/{}".format(tweet_id))
    
        # Check for a successful response
        if response.status_code == 200:
            # If the deletion was successful on Twitter, delete the record from the tweets table
            sql = "DELETE FROM tweets WHERE id = %s"
            cursor.execute(sql, (table_id,))

            # Set is_published to false for the corresponding note in the notes table
            update_note_cmd = "UPDATE notes SET is_published = false WHERE id = %s"
            cursor.execute(update_note_cmd, (note_id,))
            
            deleted_ids.append(table_id)  # adding the id to the deleted_ids list
        else:
            print(colored(f"FAILED TO DELETE TWEET WITH ID {table_id}", 'red'))
            print(response)

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"TWEETS WITH IDS {deleted_ids} SUCCESSFULLY DELETED", 'cyan'))

def fn_delete_linkedin_posts_by_note_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    note_ids_to_delete = [int(id_str) for id_str in called_function_arguments_dict.get('ids').split('_')]
    deleted_note_ids = []  # to store the note ids for which tweets have been successfully deleted

    oauth = get_oauth_session()

    for note_id in note_ids_to_delete:
        # Fetch the corresponding tweet_id(s) from the database
        select_cmd = "SELECT id, tweet_id FROM tweets WHERE note_id = %s"
        cursor.execute(select_cmd, (note_id,))
        results = cursor.fetchall()

        if not results:
            print(colored(f"No tweets found for note ID {note_id}", 'red'))
            continue

        all_tweets_deleted = True  # flag to check if all tweets for a note have been successfully deleted

        for result in results:
            table_id, tweet_id = result
            time.sleep(1)
            # Delete the tweet on Twitter
            url = f"https://api.twitter.com/2/tweets/{tweet_id}"
            response = oauth.delete(url)

            # Check for a successful response
            if response.status_code == 200:
                # If the deletion was successful on Twitter, delete the record from the tweets table
                sql = "DELETE FROM tweets WHERE id = %s"
                cursor.execute(sql, (table_id,))
            else:
                print(colored(f"FAILED TO DELETE TWEET WITH ID {tweet_id} FOR NOTE ID {note_id}", 'red'))
                print(response.text)
                all_tweets_deleted = False

        if all_tweets_deleted:
            # If all tweets for a note have been successfully deleted, set the note's is_published to 0
            update_note_cmd = "UPDATE notes SET is_published = 0 WHERE id = %s"
            cursor.execute(update_note_cmd, (note_id,))

            # add the note id to the deleted_note_ids list
            deleted_note_ids.append(note_id)

    conn.commit()
    cursor.close()
    conn.close()

    print(colored(f"TWEETS FOR NOTE IDS {deleted_note_ids} SUCCESSFULLY DELETED", 'cyan'))

def fn_delete_queued_linkedin_posts_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    ids_to_delete = called_function_arguments_dict.get('ids').split('_')
    deleted_ids = []  # to store the successfully deleted tweet ids

    for table_id in ids_to_delete:
        # Fetch the corresponding tweet_id from the database
        select_cmd = "SELECT id FROM queued_tweets WHERE id = %s"
        cursor.execute(select_cmd, (table_id,))
        result = cursor.fetchone()

        if result is None:
            print(colored(f"No queued tweet found with ID {table_id}", 'red'))
            continue

        sql = "DELETE FROM queued_tweets WHERE id = %s"
        cursor.execute(sql, (table_id,))
        deleted_ids.append(table_id)  # adding the id to the deleted_ids list

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"QUEUED TWEETS WITH IDS {deleted_ids} SUCCESSFULLY DELETED", 'cyan'))

def fn_delete_queued_linkedin_posts_by_note_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    note_ids_to_delete = [int(id_str) for id_str in called_function_arguments_dict.get('ids').split('_')]
    deleted_note_ids = []  # to store the note ids for which tweets have been successfully deleted

    for note_id in note_ids_to_delete:
        # Fetch the corresponding tweet_id(s) from the database
        select_cmd = "SELECT id FROM queued_tweets WHERE note_id = %s"
        cursor.execute(select_cmd, (note_id,))
        results = cursor.fetchall()

        if not results:
            print(colored(f"No tweets found for note ID {note_id}", 'red'))
            continue

        sql = "DELETE FROM queued_tweets WHERE note_id = %s"
        cursor.execute(sql, (note_id,))
        deleted_note_ids.append(note_id)

    conn.commit()
    cursor.close()
    conn.close()

    print(colored(f"QUEUED TWEETS FOR NOTE IDS {deleted_note_ids} SUCCESSFULLY DELETED", 'cyan'))

def fn_delete_spaced_linkedin_posts_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    ids_to_delete = called_function_arguments_dict.get('ids').split('_')
    deleted_ids = []  # to store the successfully deleted tweet ids

    for table_id in ids_to_delete:
        # Fetch the corresponding tweet_id from the database
        select_cmd = "SELECT id FROM spaced_tweets WHERE id = %s"
        cursor.execute(select_cmd, (table_id,))
        result = cursor.fetchone()

        if result is None:
            print(colored(f"No spaced tweet found with ID {table_id}", 'red'))
            continue

        sql = "DELETE FROM spaced_tweets WHERE id = %s"
        cursor.execute(sql, (table_id,))
        deleted_ids.append(table_id)  # adding the id to the deleted_ids list

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"SPACED TWEETS WITH IDS {deleted_ids} SUCCESSFULLY DELETED", 'cyan'))

def fn_delete_spaced_linkedin_posts_by_note_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    note_ids_to_delete = [int(id_str) for id_str in called_function_arguments_dict.get('ids').split('_')]
    deleted_note_ids = []  # to store the note ids for which tweets have been successfully deleted

    for note_id in note_ids_to_delete:
        # Fetch the corresponding tweet_id(s) from the database
        select_cmd = "SELECT id FROM spaced_tweets WHERE note_id = %s"
        cursor.execute(select_cmd, (note_id,))
        results = cursor.fetchall()

        if not results:
            print(colored(f"No tweets found for note ID {note_id}", 'red'))
            continue

        sql = "DELETE FROM spaced_tweets WHERE note_id = %s"
        cursor.execute(sql, (note_id,))
        deleted_note_ids.append(note_id)

    conn.commit()
    cursor.close()
    conn.close()

    print(colored(f"SPACED TWEETS FOR NOTE IDS {deleted_note_ids} SUCCESSFULLY DELETED", 'cyan'))


def get_active_access_token_and_linkedin_id():

    def get_access_code_from_db():
        cursor = conn.cursor()

        cursor.execute("SELECT access_code FROM linkedin_access_codes ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        return row[0] if row else None

    def generate_new_access_code():
        url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={LINKEDIN_CLIENT_ID}&redirect_uri={LINKEDIN_REDIRECT_URL}&state=foobar&scope=r_liteprofile%20r_emailaddress%20w_member_social"
        print(colored("Click here to generate new access code: " + url, 'cyan'))

        user_input = input("Have you authorized the new access code? (yes/no): ")

        if user_input.lower() != 'yes':
            print("Please authorize the new access code before proceeding.")
            return None

        new_access_code = get_access_code_from_db()

        if new_access_code is None:
            print("No access code found in the database. Please try again.")
            return None

        return new_access_code

    def generate_new_access_token(access_code):
        data = {
            'grant_type': 'authorization_code',
            'code': access_code,
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET,
            'redirect_uri': LINKEDIN_REDIRECT_URL
        }
        response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            tokens_file = f"{parent_dir}/files/tokens/linkedin_access_token.txt"
            with open(tokens_file, 'w') as file:
                file.write(access_token)
            return access_token
        else:
            return None

    def check_if_access_token_works(access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
        if response.status_code == 200:
            linkedin_id = response.json().get('id')
            return True, linkedin_id
        else:
            print("Invalid or expired token. Please generate a new one.")
            return False, None

    tokens_file = f"{parent_dir}/files/tokens/linkedin_access_token.txt"
    linkedin_id = None
    access_token = None
    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as file:
            access_token = file.read()
            does_it_work, linkedin_id = check_if_access_token_works(access_token)
            if does_it_work == False:
                access_token = None

    if access_token is None:
        access_code = generate_new_access_code()
        if access_code is not None:
            access_token = generate_new_access_token(access_code)
            if access_token is not None:
                does_it_work, linkedin_id = check_if_access_token_works(access_token)
                if does_it_work == False:
                    print("Newly generated access token is invalid or expired.")
                    return

    if access_token is None:
        print("Failed to generate access token.")
        return

    return access_token, linkedin_id

def post_note_to_linkedin(note_id, note_text, media_url):

    access_token, linkedin_id = get_active_access_token_and_linkedin_id()

    headers = {
	'Authorization': 'Bearer ' + access_token,
	'Content-Type': 'application/json',
	'X-Restli-Protocol-Version': '2.0.0'
    }

    data = {
	'author': f"urn:li:person:{linkedin_id}",  # replace with your LinkedIn ID
	'lifecycleState': 'PUBLISHED',
	'specificContent': {
	    'com.linkedin.ugc.ShareContent': {
		'shareCommentary': {
		    'text': ''
		},
		'shareMediaCategory': 'NONE'
	    }
	},
	'visibility': {
	    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
	}
    }

    response = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, data=json.dumps(data))


    if response.status_code != 429:
	    print(colored("Rate limit is not exceeded yet", 'cyan'))

    return

def get_media_id_after_generating_image_and_uploading_to_linkedin(prompt, size, note_id, media_url: str = None):

    if media_url is None:

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPEN_AI_API_KEY}"
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": size
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # Return the response data as JSON
        response_data = response.json()

        media_url = response_data['data'][0]['url']

    # Download the image from the URL
    downloaded_image = requests.get(media_url)

    if downloaded_image.status_code != 200:
        raise Exception("Failed to download image from URL: {} {}".format(downloaded_image.status_code, downloaded_image.text))

    image_content = downloaded_image.content

    # Upload the media to Google Cloud Storage
    storage_client = storage.Client.from_service_account_json(path_to_service_account_file)
    bucket = storage_client.get_bucket(NOTE_IMAGE_STORAGE_BUCKET_NAME)

    filename = f"{note_id}_{datetime.datetime.now(tz).strftime('%Y%m%d_%H%M%S')}"

    blob = bucket.blob(f"{filename}.jpg")
    blob.upload_from_string(
        image_content,
        content_type='image/jpeg'
    )
    print(f"Image uploaded to {blob.public_url}")
    media_url = blob.public_url

    base64_image_content = base64.b64encode(image_content).decode('utf-8')

    # Upload the media to Twitter
    media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"

    oauth = get_oauth_session()
    image_upload_response = oauth.post(media_upload_url, data={"media_data": base64_image_content})

    if image_upload_response.status_code == 200:
        json_image_upload_response = image_upload_response.json()
        print(json_image_upload_response)
        media_id = json_image_upload_response["media_id_string"]
        return {"media_url": media_url, "media_id": media_id}
    else:
        print(colored('Image upload to twitter failed','red'))



