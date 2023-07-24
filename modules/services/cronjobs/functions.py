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
import pytz

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

CRONJOBS = {
        "publishQueuedTweets": os.path.join(script_dir, "commands", "publishQueuedTweets.py"),
        "publishSpacedTweets": os.path.join(script_dir, "commands", "publishSpacedTweets.py"),
        "improviseTweets": os.path.join(script_dir, "commands", "improviseTweets.py"),
        }

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

def fn_list_functions():
    functions = [
            {
                "function": "inspect_cronjob_logs_by_id",
                "description": "Inspects cron job logs by id",
            },
            {
                "function": "list_cronjobs",
                "description": "Lists the user's cronjobs",
            },
            {
                "function": "list_cronjob_logs",
                "description": "Lists the user's cronjob logs",
            },
            {
                "function": "clear_cronjob_logs",
                "description": "Clears, deletes, truncates the user's cronjob logs",
            },
            {
                "function": "activate_cronjobs",
                "description": "Activates the user's cronjobs",
            },
            {
                "function": "deactivate_cronjobs",
                "description": "Deactivates the user's cronjobs",
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
    print(colored('CRONJOBS MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_inspect_cronjob_logs_by_id(called_function_arguments_dict):
    cursor = conn.cursor()
    id = int(called_function_arguments_dict.get('id', 0))

    if id != 0:
        query = "SELECT * FROM cronjob_logs WHERE id=%s"
        cursor.execute(query, (id,))
        
        # Fetch all columns
        columns = [col[0] for col in cursor.description]

        # Fetch the row
        row = cursor.fetchone()
        
        if row is None:
            print(colored("No result found", 'cyan'))
            return
        
        result = dict(zip(columns, row))

        # Convert 'value' to int if it's present
        if 'value' in result:
            result['value'] = int(result['value'])

        # Convert executed_at to IST
        if 'executed_at' in result:
            ist = pytz.timezone('Asia/Kolkata')
            result['executed_at'] = result['executed_at'].replace(tzinfo=pytz.utc).astimezone(ist)

        # If error_logs is present and is JSON, parse it and pretty print it
        if 'error_logs' in result:
            try:
                error_logs = json.loads(result['error_logs'])
                result['error_logs'] = json.dumps(error_logs, indent=4)
            except json.JSONDecodeError:
                pass

        # Close the cursor but keep the connection open if it's needed elsewhere
        cursor.close()

        # Print the heading
        heading = f"CRONJOB LOG DETAIL FOR ID {id}"
        print()
        print(colored(heading, 'cyan'))

        # Print each item of the result
        for key, value in result.items():
            print(colored(f"{key}: {value}", 'cyan'))

    else:
        print(colored("Please provide a valid ID", 'red'))

def fn_list_cronjobs():
    print(colored('Listing cronjobs', 'cyan'))
    with CronTab(user=getpass.getuser()) as cron:
        jobs = list(cron)
        if not jobs:
            print(colored("No cron jobs found", 'cyan'))
            return
        for job in jobs:
            print(job)

def fn_list_cronjob_logs(called_function_arguments_dict):
    cursor = conn.cursor()
    limit = int(called_function_arguments_dict.get('limit', 10))

    query = "SELECT * FROM cronjob_logs ORDER BY id DESC LIMIT %s"
    cursor.execute(query, (limit,))

    # Fetch all columns
    columns = [col[0] for col in cursor.description]

    # Fetch all rows
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]

    if not result:
        print(colored("No result found", 'cyan'))
        return

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)

    if 'value' in df.columns:
        df['value'] = df['value'].astype(int)

    # Truncate error_logs column to 30 characters and add "...." if it exceeds that limit
    if 'error_logs' in df.columns:
        df['error_logs'] = df['error_logs'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)

    # Close the cursor but keep the connection open if it's needed elsewhere
    cursor.close()

    # Construct and print the heading
    heading = f"CRONJOB LOGS (Most recent {limit} records)"
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_clear_cronjob_logs():
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE cronjob_logs")
        conn.commit()
        print(colored("Successfully cleared cronjob_logs", 'cyan'))
    except mysql.connector.Error as err:
        print(f"Error occurred: {err}")
    finally:
        cursor.close()

def fn_activate_cronjobs():
    print('Activating cronjobs')
    with CronTab(user=getpass.getuser()) as cron:
        for job_name, script_path in CRONJOBS.items():
            print(script_path)
            job = cron.new(command=f'{parent_dir}/botvenv/bin/python {script_path}', comment=job_name)
            job.setall('0 * * * *') # this sets the cron job to run every hour on the hour
            cron.write()

def fn_deactivate_cronjobs():
    print('Deactivating cronjobs')
    with CronTab(user=getpass.getuser()) as cron:
        for job_name in CRONJOBS.keys():
            cron.remove_all(comment=job_name)
            cron.write()

