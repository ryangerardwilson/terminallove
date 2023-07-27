import mysql.connector
import datetime
from datetime import timedelta
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


def clean_google_cloud_storage():
    # Create a new Cursor
    cursor = conn.cursor()

    print('AOAOAOAO', datetime.datetime.now(tz))
    executed_at = datetime.datetime.now(tz)
    formatted_executed_at = executed_at.strftime("%Y-%m-%d %H:%M:%S")
    print('formatted executed at: ', formatted_executed_at)
    error_logs = []

    # Log the start of the job
    cursor.execute(
        "INSERT INTO cronjob_logs (job_description, executed_at, error_logs) VALUES (%s, %s, %s)",
        ("Executing cleanGoogleCloudStorage.py", formatted_executed_at, json.dumps([]))
    )

    log_id = cursor.lastrowid

    try:

        """
        STEP I - GET ALL URLS FROM GOOGLE CLOUD STORAGE
        """


        def list_recent_blobs(bucket_name, delimiter=None):
            storage_client = storage.Client.from_service_account_json(path_to_service_account_file)

            blobs = storage_client.list_blobs(
                bucket_name, delimiter=delimiter
            )


            # We are excluding the preceeding 24 hours to avoid a situation where is cronjob deletes a URL that has just been created but hasnt been set to the notes table yet, at the time when improviseTweets.py executes
            x_days_ago = datetime.datetime.now(tz) - timedelta(days=10)
            one_day_ago = datetime.datetime.now(tz) - timedelta(days=1)
            blob_urls = []

            for blob in blobs:
                # extract the date from the blob name
                print(blob.public_url)
                date_str = blob.name.split('_')[1].split('.')[0]  # split on underscore and then on dot
                blob_date = datetime.datetime.strptime(date_str, '%Y%m%d').replace(tzinfo=tz)

                if x_days_ago <= blob_date <= one_day_ago:
                    blob_urls.append(blob.public_url)
            
            return blob_urls

        bucket_name = NOTE_IMAGE_STORAGE_BUCKET_NAME
        blob_urls = list_recent_blobs(bucket_name)

        # print the list of blob urls
        for url in blob_urls:

            print(url)

        """
        STEP II - IDENTIFY WHICH URLS ARE NOT PRESENT IN THE NOTES TABLE, AND DELETE THEM FROM GOOGLE CLOUD
        """

        def delete_orphan_blobs(blob_urls):
            # Fetch URLs from the notes table
            cursor.execute("SELECT media_url FROM notes")
            note_urls = [item[0] for item in cursor.fetchall()]  # extracting the urls from the result

            # Delete blobs not found in the notes table
            storage_client = storage.Client.from_service_account_json(path_to_service_account_file)

            for blob_url in blob_urls:
                if blob_url not in note_urls:

                    # Extract blob name from the URL
                    blob_name = blob_url.split('/')[-1]  # the blob name is the last part of the URL

                    # Get bucket and blob
                    bucket = storage_client.get_bucket(bucket_name)
                    blob = bucket.blob(blob_name)

                    # Delete the blob
                    blob.delete()

                    print(f"Deleted blob: {blob_name}")

        delete_orphan_blobs(blob_urls)

        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("cleanGoogleCloudStorage.py", json.dumps(error_logs), log_id)
        )

    except Exception as e:
        print(e)
        error_logs.append(str(e))  # Append the error to the error_logs list
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("cleanGoogleCloudStorage.py failed", json.dumps(error_logs), log_id)
        )

    finally:
        conn.commit()

if __name__ == '__main__':
    clean_google_cloud_storage()

