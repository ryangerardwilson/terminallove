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
import json
from crontab import CronTab
import getpass

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

CRONJOBS = {
        "publishQueuedTweets": os.path.join(script_dir, "publishQueuedTweets.py")
        }

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

def fn_list_cronjob_logs(called_function_arguments_dict):
    print('Listing cronjob logs')
    with CronTab(user=getpass.getuser()) as cron:
        jobs = list(cron)
        if not jobs:
            print("No cron jobs found.")
            return
        for job in jobs:
            print(job)

def fn_activate_cronjobs():
    print('Activating cronjobs')
    with CronTab(user=getpass.getuser()) as cron:
        for job_name, script_path in CRONJOBS.items():
            job = cron.new(command=f'python3 {script_path}', comment=job_name)
            job.hour.every(1) # this is just an example, you can set your own time
            cron.write()

def fn_deactivate_cronjobs():
    print('Deactivating cronjobs')
    with CronTab(user=getpass.getuser()) as cron:
        for job_name in CRONJOBS.keys():
            cron.remove_all(comment=job_name)
            cron.write()

