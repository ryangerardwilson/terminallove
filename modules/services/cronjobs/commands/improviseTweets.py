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
import requests
import textwrap
import base64
from google.cloud import storage

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

NOTE_IMAGE_STORAGE_BUCKET_NAME=os.getenv('NOTE_IMAGE_STORAGE_BUCKET_NAME')
GOOGLE_SERVICE_ACCOUNT_KEY=os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
path_to_service_account_file=os.path.join(parent_dir,'files/tokens/',GOOGLE_SERVICE_ACCOUNT_KEY)

OPEN_AI_API_KEY=os.getenv('OPEN_AI_API_KEY')
GPT_MODEL=os.getenv('GPT_MODEL')

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


def improvise_tweets():

    cursor = conn.cursor()

    error_logs = []
    # Log the start of the job
    cursor.execute(
        "INSERT INTO cronjob_logs (job_description, executed_at, error_logs) VALUES (%s, %s, %s)",
        ("Executing improviseTweets.py", datetime.datetime.now(tz), json.dumps([]))
    )

    # Remember the ID of the log entry
    log_id = cursor.lastrowid
    conn.commit()



    # Step 1 - Check the following conditions:
    # (a) No tweets have been published in the last hour.
    # (b) No tweets are currently queued to be published.
    # (c) No tweets are scheduled to be published in the next hour.

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM tweets WHERE posted_at > %s LIMIT 1)",
        (datetime.datetime.now(tz) - datetime.timedelta(hours=TWITTER_NOTE_SPACING),)
    )
    recently_published_tweets_exists = cursor.fetchone()[0] == 1

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM queued_tweets LIMIT 1)"
    )
    queued_tweets_exists = cursor.fetchone()[0] == 1

    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM spaced_tweets WHERE scheduled_at < %s AND scheduled_at > %s LIMIT 1)",
        (datetime.datetime.now(tz), datetime.datetime.now(tz) + datetime.timedelta(hours=TWITTER_NOTE_SPACING))
    )
    upcoming_tweets_exists = cursor.fetchone()[0] == 1

    print(recently_published_tweets_exists, queued_tweets_exists, upcoming_tweets_exists)

    if not recently_published_tweets_exists and not queued_tweets_exists and not upcoming_tweets_exists:

        try:
            # Step 2 - Randowmly select one of the last 10 published notes, and use AI to rephrase that
            cursor.execute(
                "SELECT * FROM (SELECT * FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 10) AS last_10_published_notes ORDER BY RAND() LIMIT 1"
            )
            random_note = cursor.fetchone()
            random_note_text = random_note[1]
            print('aaa', random_note_text)
            print()
            print()
            prompt = f"Use vivid imagery and tell me a similar story, using fictional characters and short sentences: {random_note_text}"

            ai_generated_note_text = get_completion(prompt)
            print('bbb', ai_generated_note_text)
            print()
            print()

            formatted_text = reformat_text(ai_generated_note_text, 3)
            print(formatted_text)

            # Step 3 - Inset it into notes, and set the is_organic value of the note to false
            insert_cmd = (
                "INSERT INTO notes (note, is_published, created_at, updated_at, is_organic) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            is_published = False
            is_organic = False
            created_at = updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_cmd, (formatted_text, is_published, created_at, updated_at, is_organic))
            conn.commit()
            note_id = cursor.lastrowid

            # Step 4 - Use the tweet out note pipeline to tweet it out
            print('124')
            generate_ai_image_for_ai_note(note_id)
            print('125')
            tweet_out_ai_note(note_id)

            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s WHERE id = %s",
                ("improviseTweets.py", log_id)
            )
            update_cmd = ("UPDATE notes SET is_published = 1 WHERE id = %s")
            cursor.execute(update_cmd, (note_id,))
        except:
            # Assume error_logs is a dictionary, add "Something went wrong" into error_logs
            message = "Something went wrong"
            error_logs.append(message)

            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("improviseTweets.py", json.dumps(error_logs), log_id)
            )
    else:
        print('Too soon to imrpovise')
        cursor.execute(
             "UPDATE cronjob_logs SET job_description = %s WHERE id = %s",
             ("improviseTweets.py", log_id)
        )

    if rate_limit_hit:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("improviseTweets.py", json.dumps(error_logs), log_id)
        )
    conn.commit()

def get_completion(prompt):
    
    url = "https://api.openai.com/v1/chat/completions"
    messages = [
            {"role": "system", "content": "You are a helpful assistant."}, 
            {"role": "user", "content": prompt}
            ]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPEN_AI_API_KEY}",
    }
    data = {
        "model": GPT_MODEL,
        "messages": messages,
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:  # Check if the request was successful
        response_content = response.json()  
        assistant_message = response_content['choices'][0]['message']['content']
        return assistant_message  # Returns the content of the assistant's message
    else:
        return f"API call failed with status code {response.status_code} and error: {response.text}"

def reformat_text(text, min_paragraphs):
    # combine all text into one paragraph
    combined_text = text.replace("\n\n", " ").replace("\n", " ")

    # split the combined text into sentences
    sentences = combined_text.split('. ')

    # Add the '.' back into each sentence except for the last one
    sentences = [sentence + '.' for sentence in sentences[:-1]] + [sentences[-1]]

    # combine sentences into new paragraphs of less than 280 characters
    formatted_paragraphs = []
    current_paragraph = ""
    for sentence in sentences:
        if len(current_paragraph) + len(sentence) > 270:  # +10 for prefix
            formatted_paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
        else:
            current_paragraph += " " + sentence

    # don't forget the last paragraph
    if current_paragraph:
        formatted_paragraphs.append(current_paragraph.strip())

    # if not enough paragraphs, split the longest one
    while len(formatted_paragraphs) < min_paragraphs:
        max_len_idx = max(range(len(formatted_paragraphs)), key=lambda index: len(formatted_paragraphs[index]))
        long_paragraph = formatted_paragraphs.pop(max_len_idx)
        half = len(long_paragraph) // 2
        first_half = long_paragraph[:half].rsplit('. ', 1)[0] + '.'
        second_half = long_paragraph[half:].lstrip()
        formatted_paragraphs.extend([first_half, second_half])

    total = len(formatted_paragraphs)
    # add the prefix
    formatted_paragraphs = ["{" + f"{i+1}/{total}" + "} " + para for i, para in enumerate(formatted_paragraphs)]

    return '\n\n'.join(formatted_paragraphs)

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

def generate_ai_image_for_ai_note(note_id):
    
    cursor = conn.cursor()
    print('279')
    # Get the media_url before updating the note
    cursor.execute("SELECT note, is_published, media_url FROM notes WHERE id = %s", (note_id,))
    result = cursor.fetchone()
    print('283')
    if result is not None:
        note_text, is_published, old_media_url = result
        if is_published == 1:
            print(colored(f"Note id {note_id} not deleted. Please delete publications of note id {note_id} before adding/ updating media", 'red'))
            return
        paragraphs = note_text.split("\n\n")
        first_paragraph = paragraphs[0]
        print('291')
        media_url = get_media_url_after_generating_image_and_uploading_to_cloud_storage(f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {first_paragraph}", "256x256", note_id)
        print()
        print(colored(f"New media_url for note id {note_id} is: {media_url}", 'cyan'))
        print()
        # Update the media_url column of the row with new media_url
        cursor.execute("UPDATE notes SET media_url = %s WHERE id = %s", (media_url, note_id))

    conn.commit()
    cursor.close()

def get_media_url_after_generating_image_and_uploading_to_cloud_storage(prompt, size, note_id):

    print('304')
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

    open_ai_media_url = response_data['data'][0]['url']

    # Download the image from the URL
    downloaded_image = requests.get(open_ai_media_url)

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
    media_url = blob.public_url

    return media_url

def tweet_out_ai_note(note_id):
    print('359')
    cursor = conn.cursor()
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')

    inserted_tweets = []
    media_url = None
    media_id = None

    select_cmd = ("SELECT note, media_url FROM notes WHERE id = %s")
    cursor.execute(select_cmd, (note_id,))
    note_result = cursor.fetchone()
    note_text, media_url = note_result

    paragraphs = note_text.split("\n\n")

    cursor.execute("SELECT tweet FROM tweets")
    previous_tweets = {row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT tweet FROM queued_tweets")
    queued_tweets = {row[0] for row in cursor.fetchall()}

    previous_tweet_id = None

    latest_tweet_time = None
    cursor.execute("SELECT MAX(posted_at) FROM tweets")
    result = cursor.fetchone()
    if result is not None and result[0] is not None:
        latest_tweet_time = result[0]

    latest_different_note_scheduled_time = None
    cursor.execute("SELECT MAX(scheduled_at) FROM spaced_tweets WHERE note_id != %s", (note_id,))
    result = cursor.fetchone()
    if result is not None and result[0] is not None:
        latest_different_note_scheduled_time = result[0]

    rate_limit_hit = False
    
    for i, paragraph in enumerate(paragraphs, 1):
        print('i: ', i)
        print('397')
        if not paragraph.strip():
            print(colored(f"Skipping empty paragraph {i}", 'red'))
            if i == 1:
                print(colored('You may have forgotten to save the note', 'red'))
            continue

        if len(paragraph) > 280:
            print(colored(f"Paragraph {i} is longer than 280 characters by {len(paragraph) - 280} characters. Not tweeting anything", 'red'))
            return

        if paragraph in previous_tweets:
            print(colored(f"Paragraph {i} has already been posted. Not tweeting anything", 'red'))
            return
        print('411')
        check_cmd = ("SELECT tweet FROM tweets WHERE tweet = %s")
        cursor.execute(check_cmd, (paragraph,))
        if cursor.fetchone() is not None:
            print(colored(f"Paragraph {i} has already been posted", 'red'))
            continue

        if rate_limit_hit:
            tweet_failed_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            queue_insert_cmd = ("INSERT INTO queued_tweets (note_id, tweet, tweet_failed_at) VALUES (%s, %s, %s)")
            cursor.execute(queue_insert_cmd, (note_id, paragraph, tweet_failed_at))
            conn.commit()
            print(colored(f"Paragraph {i} has been queued due to rate limit hit.", 'yellow'))
            continue
        
        payload = {"text": paragraph}
        print('413')
        if previous_tweet_id is not None:
            payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}

        oauth = get_oauth_session()
        print('418')
        if i == 1:
            print('421') 
            media_info = get_media_id_after_generating_image_and_uploading_to_twitter(f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {paragraph}", "256x256", note_id)
            print('423')
            # Access the image URL and media ID
            media_url = media_info["media_url"]
            media_id = media_info["media_id"]
            payload["media"] = {"media_ids": [media_id]}
            print('428')
            update_cmd = ("UPDATE notes SET media_url = %s WHERE id = %s")
            cursor.execute(update_cmd, (media_url, note_id))
            conn.commit()
        else:
            media_url = None
            media_id = None
        print('433')
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
        if response.status_code == 429:  # Rate limit exceeded
            rate_limit_limit = response.headers.get('x-rate-limit-limit')
            rate_limit_remaining = response.headers.get('x-rate-limit-remaining')
            rate_limit_reset = response.headers.get('x-rate-limit-reset')

            rate_limit_reset_date = datetime.datetime.utcfromtimestamp(int(rate_limit_reset))
            rate_limit_reset_date = rate_limit_reset_date.replace(tzinfo=pytz.utc).astimezone(tz)

            error_message = f"Rate limit exceeded. Improvised tweets have been queued. Rate limit ceiling: {rate_limit_limit}, rate limit remaining: {rate_limit_remaining}, rate limit reset: {rate_limit_reset_date}"
            rate_limit_hit = True
            error_logs.append(error_message)
            tweet_failed_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            queue_insert_cmd = ("INSERT INTO queued_tweets (note_id, tweet, tweet_failed_at, media_id) VALUES (%s, %s, %s, %s)")
            cursor.execute(queue_insert_cmd, (note_id, paragraph, tweet_failed_at, media_id))
            conn.commit()
            rate_limit_hit = True
            continue

        if response.status_code != 201:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

        json_response = response.json()
        print('449')
        if 'data' in json_response:
            print('451')
            tweet_id = json_response['data']['id']
            previous_tweet_id = tweet_id
            posted_at = datetime.datetime.now(tz)
            insert_cmd = ("INSERT INTO tweets (tweet, tweet_id, posted_at, note_id, media_id) VALUES (%s, %s, %s, %s, %s)")
            cursor.execute(insert_cmd, (paragraph, tweet_id, posted_at, note_id, media_id))
            conn.commit()

            inserted_tweets.append({
                'tweet': paragraph,
                'tweet_id': tweet_id,
                'posted_at': posted_at,
                'note_id': note_id,
                'media_id':media_id,
            })

    if inserted_tweets:
        published_at = datetime.datetime.now(tz)
        print(published_at)
        print(media_url)
        print(note_id)

        # Mark the note as published after all its paragraphs have been successfully tweeted
        update_cmd = ("UPDATE notes SET is_published = 1, published_at = %s, media_url = %s WHERE id = %s")
        cursor.execute(update_cmd, (published_at, media_url, note_id,))
        conn.commit()
        df = pd.DataFrame(inserted_tweets)
        df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

        print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    cursor.close()

def get_media_id_after_generating_image_and_uploading_to_twitter(prompt, size, note_id):

    print('487')
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


if __name__ == '__main__':
    improvise_tweets()

