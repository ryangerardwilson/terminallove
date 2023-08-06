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

def fn_list_linkedin_module_functions(called_function_arguments_dict):

    functions = [
        {
            "function": "list_linkedin_posts",
            "description": "Lists the user's LinkedIn posts",
        },
        {
            "function": "list_rate_limits",
            "description": "Lists LinkedIn rate limits",
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

def fn_list_linkedin_rate_limits(called_function_arguments_dict):
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
    else:
        print(colored("Rate limit exceeded","red"))

    return

def fn_list_linkedin_posts(called_function_arguments_dict):

    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 20))

    if limit < 20:
        limit = 20

    query = "SELECT * FROM linkedin_posts ORDER BY id DESC LIMIT %s"
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

    # Truncate note column to 300 characters and add "...." if it exceeds that limit
    if 'post' in df.columns:
        df['post'] = df['post'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Convert posted_at to IST
    if 'posted_at' in df.columns:
        ist = pytz.timezone('Asia/Kolkata')
        df['posted_at'] = df['posted_at'].apply(lambda x: x.replace(tzinfo=pytz.utc).astimezone(ist))

    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"LINKEDIN POSTS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

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



