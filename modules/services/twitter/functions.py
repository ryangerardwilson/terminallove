import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
import subprocess
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
load_dotenv(os.path.join(parent_dir, '.env'))

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

def fn_open_tweetpad():
    dir_path = os.path.join(parent_dir, "files")
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, "tweetpad.txt")
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as fp:
            pass  # Just creating the file.
    print('Open tweetpad')
    subprocess.call(["vim", file_path])

def fn_save_tweetpad():
    file_path = os.path.join(parent_dir, "files", "tweetpad.txt")
    if not os.path.isfile(file_path):
        print('File does not exist.')
        return
    with open(file_path, 'r') as fp:
        note_content = fp.read()
    insert_cmd = (
        "INSERT INTO tweetpads (note, is_published, created_at, updated_at) "
        "VALUES (%s, %s, %s, %s)"
    )
    is_published = False  # Default value.
    created_at = updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp.
    cursor = conn.cursor()
    cursor.execute(insert_cmd, (note_content, is_published, created_at, updated_at))
    conn.commit()
    cursor.close()
    print('Saved tweetpad to database.')

def fn_list_tweets():

    cursor = conn.cursor
    print('List tweets')

def fn_list_scheduled_tweets():
     
     cursor = conn.cursor
     print('List scheduled tweets')

def fn_tweet(called_function_arguments_dict):

    cursor = conn.cursor
    print('tweet')

    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_schedule_tweet(called_function_arguments_dict):

    cursor = conn.cursor
    print('schedule tweet')
    
    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_edit_tweet(called_function_arguments_dict):

    cursor = conn.cursor
    print('edit tweet')
    
    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

def fn_delete_tweets_by_ids(called_function_arguments_dict):

    cursor = conn.cursor
    print('delete tweets by ids')

    # Set default values
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)
    print(date)

