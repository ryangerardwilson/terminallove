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


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

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

