import mysql.connector
import datetime
import pytz
import pandas as pd
from termcolor import colored
import os
from tabulate import tabulate
from dotenv import load_dotenv

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

def fn_list_time_module_functions(called_function_arguments_dict):
    functions = [
            {
                "function": "schedule_event",
                "description": "Log an event the user needs to attend to",
            },
            {
                "function": "list_events",
                "description": "Lists the user's calendered and docketed events",
            },
            {
                "function": "update_event_by_id",
                "description": "Update an event by its id",
            },
            {
                "function": "delete_events_by_ids",
                "description": "Delete events by their ids",
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
    print(colored('TIME MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_schedule_event(called_function_arguments_dict):

    cursor = conn.cursor()

    # Set default values
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    default_time = '00:00:00'  # Change default time here

    # If "date" and "time" are not in called_function_arguments_dict, set them to the defaults
    event = called_function_arguments_dict.get('event')
    date = called_function_arguments_dict.get('date', default_date)
    time = called_function_arguments_dict.get('time', default_time)

    sql = "INSERT INTO events (event, date, time) VALUES (%s, %s, %s)"
    values = (event, date, time)

    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute(f"SELECT * FROM events WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_list_events(called_function_arguments_dict):
    cursor = conn.cursor()

    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')

    # Query to get all events sorted by date in descending order
    query = "SELECT * FROM events WHERE date >= DATE(%s) ORDER BY date DESC, time DESC"
    cursor.execute(query, (default_date,))

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_update_event_by_id(called_function_arguments_dict):

    event_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    update_columns = []
    values = []

    for key, value in called_function_arguments_dict.items():
        if value is not None:
            update_columns.append(f"{key} = %s")
            values.append(value)

    update_columns = ', '.join(update_columns)
    values.append(event_id)  # Add event_id to the end of values list

    sql = f"UPDATE events SET {update_columns} WHERE id = %s"

    cursor.execute(sql, values)

    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM events WHERE id = {event_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    cursor.close()
    conn.close()

    print(colored(f"Event with id {event_id} updated successfully.", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

def fn_delete_events_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()

    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for id in ids_to_delete:
        sql = "DELETE FROM events WHERE id = %s"
        cursor.execute(sql, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    print(colored(f"Events with ids {ids_to_delete} deleted successfully.", 'cyan'))
