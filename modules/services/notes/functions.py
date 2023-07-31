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
import pytz
from requests_oauthlib import OAuth1Session
from google.cloud import storage
import urllib.parse
import requests
import json
import base64

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

OPEN_AI_API_KEY=os.getenv('OPEN_AI_API_KEY')

NOTE_IMAGE_STORAGE_BUCKET_NAME=os.getenv('NOTE_IMAGE_STORAGE_BUCKET_NAME')
GOOGLE_SERVICE_ACCOUNT_KEY=os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
path_to_service_account_file=os.path.join(parent_dir,'files/tokens/',GOOGLE_SERVICE_ACCOUNT_KEY)

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

PUBLISHED_NOTE_SPACING=int(os.getenv('PUBLISHED_NOTE_SPACING'))

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

def fn_open_note(called_function_arguments_dict):
    note_id = int(called_function_arguments_dict.get('id', 0))
    cursor = conn.cursor()
    dir_path = os.path.join(parent_dir, "files")
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    if note_id == 0:
        try:
            insert_cmd = (
                "INSERT INTO notes (note, is_published, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s)"
            )
            is_published = False
            created_at = updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_cmd, ( '', is_published, created_at, updated_at))
            conn.commit()
            new_id = cursor.lastrowid
            updated_at_filename = datetime.datetime.now(tz).strftime('[U:%Y%m%d(%H%M%S)]')
            created_at_filename = datetime.datetime.now(tz).strftime('[C:%Y%m%d(%H%M%S)]')
            file_path = os.path.join(dir_path, f"note_{new_id}_{created_at_filename}_{updated_at_filename}.txt")
            with open(file_path, 'w') as fp:
                pass
        except Exception as e:
            print("An error occurred:", e)

    else:
        select_cmd = (
            "SELECT note, created_at, updated_at FROM notes WHERE id = %s"
        )
        cursor.execute(select_cmd, (note_id,))
        note, created_at, updated_at = cursor.fetchone()
        if note is None:
            print(colored(f"No record exists for id {note_id}", 'cyan'))
            return
        created_at_filename = created_at.strftime('[C:%Y%m%d(%H%M%S)]')
        updated_at_filename = updated_at.strftime('[U:%Y%m%d(%H%M%S)]')
        file_path = os.path.join(dir_path, f"note_{note_id}_{created_at_filename}_{updated_at_filename}.txt")
        with open(file_path, 'w') as fp:
            fp.write(note)

    print(colored(f"Opened note at: {file_path}",'cyan'))
    print(colored("IMPORTANT! NOTE WILL REMAIN IN LOCAL CACHE UNTILL YOU SAVE IT", 'red'))
    cursor.close()
    subprocess.call(["vim", file_path])

def fn_open_most_recent_note(called_functions_argument_dict):
    is_organic_str = called_function_arguments_dict.get('is_organic', "false")
    if is_organic_str == "false":
        is_organic = 0
    else:
        is_organic = 1

    cursor = conn.cursor()
    dir_path = os.path.join(parent_dir, "files")

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    try:
        # Get the most recent note
        if is_organic == 0:
            select_cmd = (
                "SELECT id, note, created_at, updated_at FROM notes ORDER BY id DESC LIMIT 1"
            )
        else:
            select_cmd = (
                "SELECT id, note, created_at, updated_at FROM notes WHERE is_organic = 1 ORDER BY id DESC LIMIT 1"
            )
        cursor.execute(select_cmd)
        note_id, note, created_at, updated_at = cursor.fetchone()
        if note_id is None:
            print(colored("You have no notes", 'cyan'))
            return

        created_at_filename = created_at.strftime('[C:%Y%m%d(%H%M%S)]')
        updated_at_filename = updated_at.strftime('[U:%Y%m%d(%H%M%S)]')
        file_path = os.path.join(dir_path, f"note_{note_id}_{created_at_filename}_{updated_at_filename}.txt")
        with open(file_path, 'w') as fp:
            fp.write(note)
    except Exception as e:
        print(colored("An error occurred:", 'cyan'), e)

    print(colored(f"Opened note at: {file_path}",'cyan'))
    print(colored("IMPORTANT! NOTE WILL REMAIN IN LOCAL CACHE UNTILL YOU SAVE IT", 'red'))
    cursor.close()
    subprocess.call(["vim", file_path])

def fn_open_most_recently_edited_note(called_function_arguments_dict):
    is_organic_str = called_function_arguments_dict.get('is_organic', "false")
    if is_organic_str == "false":
        is_organic = 0
    else:
        is_organic = 1

    cursor = conn.cursor()
    dir_path = os.path.join(parent_dir, "files")

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    try:
        if is_organic == 0:
            select_cmd = (
                "SELECT id, note, created_at, updated_at FROM notes ORDER BY updated_at DESC LIMIT 1"
            )
        else:
            select_cmd = (
                "SELECT id, note, created_at, updated_at FROM notes WHERE is_organic = 1 ORDER BY updated_at DESC LIMIT 1"
            )
        cursor.execute(select_cmd)
        note_id, note, created_at, updated_at = cursor.fetchone()
        if note_id is None:
            print(colored("You have no notes", 'cyan'))
            return

        created_at_filename = created_at.strftime('[C:%Y%m%d(%H%M%S)]')
        updated_at_filename = updated_at.strftime('[U:%Y%m%d(%H%M%S)]')
        file_path = os.path.join(dir_path, f"note_{note_id}_{created_at_filename}_{updated_at_filename}.txt")
        with open(file_path, 'w') as fp:
            fp.write(note)
    except Exception as e:
        print(colored("An error occurred:", 'cyan'), e)

    print(colored(f"Opened note at: {file_path}",'cyan'))
    print(colored("IMPORTANT! NOTE WILL REMAIN IN LOCAL CACHE UNTILL YOU SAVE IT", 'red'))
    cursor.close()
    subprocess.call(["vim", file_path])

def fn_save_and_close_notes():
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')

    dir_path = os.path.join(parent_dir, "files")
    cursor = conn.cursor()

    # Flag to check if there are any files to save
    is_any_file_saved = False

    for filename in os.listdir(dir_path):
        if filename.startswith("note_") and filename.endswith(".txt"):
            # Extract note_id, which is now the first element after splitting filename by '_'
            note_id = int(filename.split('_')[1])
            # Extract created_at and updated_at from the filename
            created_at_filename, updated_at_filename = filename.split('_')[2:4]

            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as fp:
                note_content = fp.read()
                print(note_content)

            # Get the modified time of the file
            mod_time = os.path.getmtime(file_path)
            # Convert it to a datetime object

            utc_time = datetime.datetime.utcfromtimestamp(mod_time)
            mod_time = utc_time.replace(tzinfo=pytz.UTC).astimezone(tz)

            # Get the updated_at time from the database for the current note_id
            select_cmd = (
                "SELECT updated_at FROM notes WHERE id = %s"
            )
            cursor.execute(select_cmd, (note_id,))
            db_updated_at, = cursor.fetchone()  # Unpack the tuple here

            # Only perform the update if the file's modified time is newer than the db_updated_at time
            print('mod_time', mod_time)
            print('db_updated_at', db_updated_at)
            mod_time = mod_time.replace(tzinfo=None)

            media_url = None
            if mod_time > db_updated_at:

                try:
                    update_cmd = (
                         "UPDATE notes SET note = %s, updated_at = %s, media_url = %s WHERE id = %s"
                        )
                    updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(update_cmd, (note_content, updated_at, media_url, note_id))
                    conn.commit() # Move this inside the loop
                except Exception as e:
                    print(f"Error updating note: {e}")

            os.remove(file_path)
            print(colored(f"Synced and closed note at: {file_path}",'cyan'))
            is_any_file_saved = True

    cursor.close()

    if is_any_file_saved:
        print(colored('Notes synced to database', 'cyan'))
    else:
        print(colored('No notes to sync', 'cyan'))

def fn_delete_local_note_cache():
   
    dir_path = os.path.join(parent_dir, "files")

    # Flag to check if there are any files to delete
    is_any_file_deleted = False

    for filename in os.listdir(dir_path):
        if filename.startswith("note_") and filename.endswith(".txt"):
            file_path = os.path.join(dir_path, filename)
            os.remove(file_path)
            print(colored(f"Deleted note at: {file_path}", 'cyan'))
            is_any_file_deleted = True

    if is_any_file_deleted:
        print(colored('Notes deleted from local cache', 'cyan'))
    else:
        print(colored('No notes to delete','cyan'))

def fn_list_notes(called_function_arguments_dict):
    is_organic_str = called_function_arguments_dict.get('is_organic', "false")
    if is_organic_str == "false":
        is_organic = 0
        query = "SELECT * FROM notes ORDER BY created_at DESC LIMIT %s"

    else:
        is_organic = 1
        query = "SELECT * FROM notes WHERE is_organic = 1 ORDER BY created_at DESC LIMIT %s"


    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 20))

    if limit < 20:
        limit = 20

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
    if 'note' in df.columns:
        df['note'] = df['note'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Truncate media_url column to 30 characters and add "...." if it exceeds that limit
    if 'media_url' in df.columns:
        df['media_url'] = df['media_url'].apply(lambda x: (x[:30] + '....') if x and len(x) > 30 else x)

    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"NOTES (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_delete_notes_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for note_id in ids_to_delete:
        # Get the media_url before deleting the note
        cursor.execute("SELECT media_url FROM notes WHERE id = %s", (note_id,))
        result = cursor.fetchone()

        if result is not None:
            media_url = result[0]

            try:
                # Split URL to get bucket name and blob name
                url_path = urllib.parse.urlparse(media_url).path
                split_path = url_path.split("/")
                bucket_name = split_path[1]
                blob_name = urllib.parse.unquote("/".join(split_path[2:]))

                # Delete the note from the database
                cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))

                # Delete the file from Google Cloud Storage
                storage_client = storage.Client.from_service_account_json(path_to_service_account_file)
                bucket = storage_client.get_bucket(NOTE_IMAGE_STORAGE_BUCKET_NAME)
                blob = bucket.blob(blob_name)

                blob.delete()
            except:
                print(f"(Media for note id {note_id} could not be deleted from storage bucket. Url is {media_url}")

        sql = "DELETE FROM notes WHERE id = %s"
        cursor.execute(sql, (note_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"NOTES WITH IDS {ids_to_delete} DELETED", 'cyan'))

def fn_add_or_update_media_to_notes_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()
    ids_to_add_media_to = called_function_arguments_dict.get('ids').split('_')

    for note_id in ids_to_add_media_to:
        # Get the media_url before updating the note
        cursor.execute("SELECT note, is_published, media_url FROM notes WHERE id = %s", (note_id,))
        result = cursor.fetchone()

        if result is not None:
            note_text, is_published, old_media_url = result
            if is_published == 1:
                print(colored(f"Note id {note_id} not deleted. Please delete publications of note id {note_id} before adding/ updating media", 'red'))
                continue
            paragraphs = note_text.split("\n\n")
            first_paragraph = paragraphs[0]

            if old_media_url is not None:
                try:
                    # Delete old_media_url from cloud storage
                    url_path = urllib.parse.urlparse(old_media_url).path
                    split_path = url_path.split("/")
                    bucket_name = split_path[1]
                    blob_name = urllib.parse.unquote("/".join(split_path[2:]))

                    # Delete the file from Google Cloud Storage
                    storage_client = storage.Client.from_service_account_json(path_to_service_account_file)
                    bucket = storage_client.get_bucket(NOTE_IMAGE_STORAGE_BUCKET_NAME)
                    blob = bucket.blob(blob_name)

                    blob.delete()
                except:
                    print(f"Deletion of old media from cloud storage failed for note id {note_id}. Old media url is: {old_media_url}")

            media_url = get_media_url_after_generating_image_and_uploading_to_cloud_storage(f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {first_paragraph}", "512x512", note_id)
            print()
            print(colored(f"New media_url for note id {note_id} is: {media_url}", 'cyan'))
            print()
            # Update the media_url column of the row with new media_url
            cursor.execute("UPDATE notes SET media_url = %s WHERE id = %s", (media_url, note_id))

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"NOTES UPDATED", 'cyan'))


def get_media_url_after_generating_image_and_uploading_to_cloud_storage(prompt, size, note_id):

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

def fn_publish_notes_by_ids(called_function_arguments_dict):

    cursor = conn.cursor()
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    ids_to_publish = called_function_arguments_dict.get('ids').split('_')

    def generate_media_for_note(note_id):
        try:
            select_cmd = (
                "SELECT note FROM notes WHERE id = %s"
            )
            cursor.execute(select_cmd, (note_id,))
            note_text, = cursor.fetchone()

            paragraphs = note_text.split("\n\n")
            first_paragraph = paragraphs[0]

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPEN_AI_API_KEY}"
            }
            data = {
                "prompt": f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {first_paragraph}",
                "n": 1,
                "size": "512x512"
            }

            response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=json.dumps(data))
            response_data = response.json()

            open_ai_media_url = response_data['data'][0]['url']
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

            # Access the image URL and media ID
            media_url = blob.public_url
            update_cmd = ("UPDATE notes SET media_url = %s WHERE id = %s")
            cursor.execute(update_cmd, (media_url, note_id))
            conn.commit()
            return True
        except Exception as e:
            print(colored(f"FAILED TO GENERATE MEDIA FOR NOTE {note_id}: ","cyan"), e)
            return False

    def tweet_out_note(note_id):
        try:
            inserted_tweets = []
            media_url = None
            media_id = None

            select_cmd = ("SELECT note, media_url FROM notes WHERE id = %s")
            cursor.execute(select_cmd, (note_id,))
            note_result = cursor.fetchone()
            note_text, media_url = note_result

            previous_tweet_id = None

            if note_text == None:
                print(colored("You can't tweet an empty note", 'red'))
                return False

            cursor.execute("SELECT tweet FROM tweets")
            previous_tweets = {row[0] for row in cursor.fetchall()}


            paragraphs = note_text.split("\n\n")
            rate_limit_hit = False

            for i, paragraph in enumerate(paragraphs, 1):
                
                if not paragraph.strip():
                    print(colored(f"Skipping empty paragraph {i}", 'red'))
                    if i == 1:
                        print(colored('You may have forgotten to save the note', 'red'))
                    continue

                if len(paragraph) > 280:
                    print(colored(f"Paragraph {i} is longer than 280 characters by {len(paragraph) - 280} characters. Not tweeting anything", 'red'))
                    return False

                if paragraph in previous_tweets:
                    print(colored(f"Paragraph {i} has already been posted. Not tweeting anything", 'red'))
                    return False

                if rate_limit_hit:
                    select_cmd = "SELECT id, tweet_id FROM tweets WHERE note_id = %s"
                    cursor.execute(select_cmd, (note_id,))
                    results = cursor.fetchall()
                    if not results:
                        print(colored(f"No published tweets to delete for note id {note_id}", 'cyan'))
                    else:
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
                                print(colored(f"Failed to delete tweet with {tweet_id} for note id {note_id}", 'cyan'))
                                print(response.text)
                        queue_insert_cmd = ("INSERT INTO queued_publications (note_id) VALUES (%s)")
                    cursor.execute(queue_insert_cmd, (note_id,))
                    conn.commit()
                    print(colored(f"Note id {note_id} has been queued due to rate limit hit.", "cyan"))
                    return False

                payload = {"text": paragraph} 
     
                if previous_tweet_id is not None: 
                    payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id} 
     
                time.sleep(1) 
                oauth = get_oauth_session() 
    
                if i == 1 and media_url != None:
                    media_id = get_media_id_after_uploading_image_to_twitter(media_url)

                if i == 1 and media_id != 0:
                    payload["media"] = {"media_ids": [media_id]}
                else:
                    media_url = None
                    media_id = None

                response = oauth.post("https://api.twitter.com/2/tweets", json=payload) 
                if response.status_code == 429:
                    rate_limit_hit = True
                    print(colored(f"Rate limit exceeded. Note is being queued", "cyan"))

                    select_cmd = "SELECT id, tweet_id FROM tweets WHERE note_id = %s"
                    cursor.execute(select_cmd, (note_id,))
                    results = cursor.fetchall()
                    if not results:
                        print(colored(f"No published tweets to delete for note id {note_id}", 'cyan'))
                    else:
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
                                print(colored(f"Failed to delete tweet with {tweet_id} for note id {note_id}", 'cyan'))
                                print(response.text)
                    queue_insert_cmd = ("INSERT INTO queued_publications (note_id) VALUES (%s)")
                    cursor.execute(queue_insert_cmd, (note_id,))
                    conn.commit()
                    print(colored(f"Note id {note_id} has been queued due to rate limit hit.", "cyan"))
                    return False
 
                if response.status_code != 201: 
                    raise Exception("Request returned an error: {} {}".format(response.status_code, response.text)) 
 
                json_response = response.json() 
 
                if 'data' in json_response: 
                    tweet_id = json_response['data']['id'] 
                    previous_tweet_id = tweet_id 
                    posted_at = datetime.datetime.now(tz) 
                    insert_cmd = ("INSERT INTO tweets (tweet, tweet_id, posted_at, note_id, media_id) VALUES (%s, %s, %s, %s, %s)") 
                    cursor.execute(insert_cmd, (paragraph, tweet_id, posted_at, note_id, media_id)) 
                    conn.commit() 
 
                    inserted_tweets.append({
                        'para': i,
                        'tweet': paragraph, 
                        'tweet_id': tweet_id, 
                        'posted_at': posted_at,
                        'note_id': note_id,
                        'media_id':media_id,
                    })

            if inserted_tweets:
                df = pd.DataFrame(inserted_tweets)
                df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)
                print(colored("\nSuccessfully tweeted out note id {note_id}\n", "cyan"))
                print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
                return True
        
        except Exception as e:
            print(colored(f"Failed to tweet out note id {note_id}: ","cyan"), e)
            return False

    def post_note_to_linkedin(note_id):
        try:
            return True
        except Exception as e:
            print(colored(f"FAILED TO GENERATE MEDIA FOR NOTE {note_id}: ","cyan"), e)
            return False

    def set_is_published_to_true(note_id):
        print(colored(f"Setting note id {note_id} as published", "cyan"))
        return True

    for note_id in ids_to_publish:
        cursor.execute("SELECT media_url FROM notes WHERE id = %s", (note_id,))
        media_url, = cursor.fetchone()

        try:

            # SQL query to fetch the most recent published note
            query = "SELECT published_at FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                published_at = result[0]
                published_at = published_at.replace(tzinfo=tz)
                now = datetime.datetime.now(tz)
                hours_since_last_published_note = (now - published_at).total_seconds() / 3600
            else:
                hours_since_last_published_note = PUBLISHED_NOTE_SPACING + 1
            if (hours_since_last_published_note < PUBLISHED_NOTE_SPACING):
                cursor.execute("INSERT INTO spaced_publications (note_id) VALUES (%s)", (note_id))
                conn.commit()
                print(colored(f"Note id {note_id} has been scheduled", 'cyan'))
                return

            has_media = False
            if media_url == None:
                has_media = generate_media_for_note(note_id)
            else:
                has_media = True
            print("LEG 1 SUCCESSFUL")

            if has_media == True:
                all_tweets_related_to_note_published = False
                all_tweets_related_to_note_published = tweet_out_note(note_id)
                
                note_posted_to_linkedin = False
                if all_tweets_related_to_note_published == True:
                    print("LEG 2 SUCCESSFUL")
                    return

                    note_posted_to_linkedin = post_note_to_linkedin(note_id)
    
            if has_media == True and all_tweets_related_to_note_published == True and note_posted_to_linkedin == True:
                set_is_published_to_true()
                print(colored(f"Note id {note_id} successfully published", "cyan"))
       
        except Exception as e:
            print('line 686 error ', e)


    return


def fn_unpublish_notes_by_ids(called_function_arguments_dict):
    print('HUHUHAHAHA')

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
        tokens_file = f"{parent_dir}/files/tokens/{TWITTER_AUTHENTICATION_KEY}"
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

def get_media_id_after_uploading_image_to_twitter(media_url):

    # Download the image from the URL
    downloaded_image = requests.get(media_url)

    if downloaded_image.status_code != 200:
        raise Exception("Failed to download image from URL: {} {}".format(downloaded_image.status_code, downloaded_image.text))

    image_content = downloaded_image.content
    base64_image_content = base64.b64encode(image_content).decode('utf-8')

    # Upload the media to Twitter
    media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"

    oauth = get_oauth_session()
    image_upload_response = oauth.post(media_upload_url, data={"media_data": base64_image_content})

    if image_upload_response.status_code == 200:
        json_image_upload_response = image_upload_response.json()
        print(json_image_upload_response)
        media_id = json_image_upload_response["media_id_string"]
    else:
        print(colored('Image upload to twitter failed','red'))
        media_id = 0
    
    return media_id



