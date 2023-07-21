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
from google.cloud import storage
import urllib.parse
import requests
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

OPEN_AI_API_KEY=os.getenv('OPEN_AI_API_KEY')

NOTE_IMAGE_STORAGE_BUCKET_NAME=os.getenv('NOTE_IMAGE_STORAGE_BUCKET_NAME')
GOOGLE_SERVICE_ACCOUNT_KEY=os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
path_to_service_account_file=os.path.join(parent_dir,'files/tokens/',GOOGLE_SERVICE_ACCOUNT_KEY)

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

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

def fn_open_most_recent_note():
    cursor = conn.cursor()
    dir_path = os.path.join(parent_dir, "files")

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    try:
        # Get the most recent note
        select_cmd = (
            "SELECT id, note, created_at, updated_at FROM notes ORDER BY id DESC LIMIT 1"
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

def fn_open_most_recently_edited_note():
    cursor = conn.cursor()
    dir_path = os.path.join(parent_dir, "files")

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    try:
        select_cmd = (
            "SELECT id, note, created_at, updated_at FROM notes ORDER BY updated_at DESC LIMIT 1"
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

    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 10))

    if limit < 10:
        limit = 10

    query = "SELECT * FROM notes ORDER BY created_at DESC LIMIT %s"
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

            media_url = get_media_url_after_generating_image_and_uploading_to_cloud_storage(f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {first_paragraph}", "256x256", note_id)
            print()
            print(colored(f"New media_url for note id {note_id} is: {media_url}", 'cyan'))
            print()
            # Update the media_url column of the row with new media_url
            cursor.execute("UPDATE notes SET media_url = %s WHERE id = %s", (media_url, note_id))

    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"NOTES WITH IDS {ids_to_add_media_to} UPDATED", 'cyan'))


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

