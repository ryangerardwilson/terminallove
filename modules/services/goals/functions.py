import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt
import pytz

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

def fn_list_goals_module_functions(called_function_arguments_dict):
    functions = [
            {
                "function": "add_goal",
                "description": "Log a goal that the user wants to achieve",
            },
            {
                "function": "list_goals",
                "description": "Lists the user's goals",
            },
            {
                "function": "update_goal_by_id",
                "description": "Update a goal by its id",
            },
            {
                "function": "delete_goals_by_ids",
                "description": "Delete goals by their ids",
            },
            {
                "function": "add_reason",
                "description": "Log why a user wants to achieve a particular goal",
            },
            {
                "function": "list_reasons_by_goal_id",
                "description": "List the reasons why the user wants to achieve a particular goal with a goal id",
            },
            {
                "function": "update_reason_by_id",
                "description": "Update a reason by its id",
            },
            {
                "function": "delete_reasons_by_ids",
                "description": "Delete reasons by their ids",
            },
            {
                "function": "add_action",
                "description": "Log actions a user will execute to achieve a particular goal",
            },
            {
                "function": "list_actions",
                "description": "Lists the actions the user will execute",
            },
            {
                "function": "list_actions_by_goal_id",
                "description": "List the actions the user will execute to achieve a particular goal with a goal id",
            },
            {
                "function": "update_action_by_id",
                "description": "Update an action by its id",
            },
            {
                "function": "delete_actions_by_ids",
                "description": "Delete actions by their ids",
            },
            {
                "function": "add_timesheet_logs",
                "description": "Log actions a user has taken on a particular day. User may indicate to mark actions with specific ids as done - in which case this function is also to be invoked",
            },
            {
                "function": "list_timesheet_logs",
                "description": "Lists logs of actions a user has taken on a particular day, or shows the user his timesheet for a particular day",
            },
            {
                "function": "delete_timesheet_logs",
                "description": "Deletes logs of actions a user has taken on a particular day. User may indicate to unmark actions with specific ids as done - in which case this function is also to be invoked",
            },
            {
                "function": "display_timesheets_line_chart",
                "description": "Plots a line chart of the users timesheet entries over the given range of days",
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
    print(colored('GOALS MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_add_goal(called_function_arguments_dict):
    cursor = conn.cursor()

    # Set default values
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')

    # If "date" is not in called_function_arguments_dict, set it to the default
    name = called_function_arguments_dict.get('name')
    date = called_function_arguments_dict.get('date', default_date)

    sql = "INSERT INTO goals (name, date) VALUES (%s, %s)"
    values = (name, date)

    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute(f"SELECT * FROM goals WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(f'ADDED GOAL', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_list_goals(called_function_arguments_dict):
    cursor = conn.cursor()

    # Query to get all events sorted by date in descending order
    cursor.execute("SELECT * FROM goals ORDER BY date DESC")

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    # df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(f'GOALS', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_update_goal_by_id(called_function_arguments_dict):
    goal_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    update_columns = []
    values = []

    for key, value in called_function_arguments_dict.items():
        if value is not None:
            update_columns.append(f"{key} = %s")
            values.append(value)

    update_columns = ', '.join(update_columns)
    values.append(goal_id)  # Add event_id to the end of values list

    sql = f"UPDATE goals SET {update_columns} WHERE id = %s"

    cursor.execute(sql, values)

    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM goals WHERE id = {goal_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    cursor.close()
    conn.close()

    print(colored(f"GOAL WITH ID {goal_id} UPDATED", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_delete_goals_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()

    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for id in ids_to_delete:
        sql = "DELETE FROM goals WHERE id = %s"
        cursor.execute(sql, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    print(colored(f"GOALS WITH IDS {ids_to_delete} DELETED", 'cyan'))


def fn_add_reason(called_function_arguments_dict):
    cursor = conn.cursor()

    # Get the values from the dictionary
    goal_id = called_function_arguments_dict.get('goal_id')
    reason = called_function_arguments_dict.get('reason')

    print('406')
    print(goal_id)
    print(type(goal_id))

    print(reason)
    print(type(reason))

    # Check if goal_id and reason are provided
    if goal_id is None or reason is None:
        raise ValueError("Both goal_id and reason must be provided")

    sql = "INSERT INTO reasons (goal_id, reason) VALUES (%s, %s)"
    values = (goal_id, reason)

    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute(f"SELECT * FROM reasons WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    print(colored(f'REASON ADDED', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    cursor.close()
    conn.close()


def fn_list_reasons_by_goal_id(called_function_arguments_dict):
    goal_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    # Query to get all events sorted by date in descending order
    cursor.execute("SELECT * FROM reasons WHERE goal_id = %s ORDER BY id DESC", (goal_id,))

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    # df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(f'REASONS FOR GOAL ID {goal_id}', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_update_reason_by_id(called_function_arguments_dict):
    reason_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    update_columns = []
    values = []

    for key, value in called_function_arguments_dict.items():
        if value is not None:
            update_columns.append(f"{key} = %s")
            values.append(value)

    update_columns = ', '.join(update_columns)
    values.append(reason_id)  # Add event_id to the end of values list

    sql = f"UPDATE reasons SET {update_columns} WHERE id = %s"

    cursor.execute(sql, values)

    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM reasons WHERE id = {reason_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    cursor.close()
    conn.close()

    print(colored(f"REASON WITH ID {reason_id} UPDATED", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_delete_reasons_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()

    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for id in ids_to_delete:
        sql = "DELETE FROM reasons WHERE id = %s"
        cursor.execute(sql, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    print(colored(f"REASONS WITH IDS {ids_to_delete} DELETED", 'cyan'))


def fn_add_action(called_function_arguments_dict):
    cursor = conn.cursor()

    # Get the values from the dictionary
    goal_id = called_function_arguments_dict.get('goal_id')
    action = called_function_arguments_dict.get('action')
    default_deadline = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    deadline = called_function_arguments_dict.get('deadline', default_deadline)

    # Check if goal_id and reason are provided
    if goal_id is None or action is None:
        raise ValueError("Both goal_id and action must be provided")

    sql = "INSERT INTO actions (goal_id, action, deadline) VALUES (%s, %s, %s)"
    values = (goal_id, action, deadline)

    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute(f"SELECT * FROM actions WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    print(colored(f'ACTION ADDED', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    cursor.close()
    conn.close()


def fn_list_actions(called_function_arguments_dict):
    cursor = conn.cursor()

    # Query to get all events sorted by date in descending order
    cursor.execute("SELECT * FROM actions WHERE is_active = 1 ORDER BY deadline ASC")

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    # df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(f'ACTIONS', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_list_actions_by_goal_id(called_function_arguments_dict):
    goal_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    # Query to get all events sorted by date in descending order
    cursor.execute("SELECT * FROM actions WHERE is_active = 1 AND goal_id = %s ORDER BY id DESC", (goal_id,))

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Convert timedelta to string in 'HH:MM:SS' format
    # df['time'] = df['time'].apply(lambda x: str(x)[-8:])

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(f'ACTIONS FOR GOAL ID {goal_id}:', 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))



def fn_update_action_by_id(called_function_arguments_dict):
    action_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    update_columns = []
    values = []

    for key, value in called_function_arguments_dict.items():
        if value is not None:
            update_columns.append(f"{key} = %s")
            values.append(value)

    update_columns = ', '.join(update_columns)
    values.append(action_id)  # Add event_id to the end of values list

    sql = f"UPDATE actions SET {update_columns} WHERE id = %s"

    cursor.execute(sql, values)

    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM actions WHERE id = {action_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    cursor.close()
    conn.close()

    print(colored(f"ACTION WITH ID {action_id} UPDATED", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_delete_actions_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()

    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for id in ids_to_delete:
        try:
            # Attempt to perform a hard delete
            sql = "DELETE FROM actions WHERE id = %s"
            cursor.execute(sql, (id,))
            print(colored(f"Action with id {id} deleted successfully.", 'cyan'))
        
        except mysql.connector.errors.IntegrityError as e:
            # If a foreign key constraint violation occurs, perform a soft delete
            if 'foreign key constraint fails' in str(e).lower():
                sql = "UPDATE actions SET is_active = 0 WHERE id = %s"
                cursor.execute(sql, (id,))
                print(colored(f"Action with id {id} marked as inactive due to foreign key constraint.", 'magenta'))

    conn.commit()

    cursor.close()
    conn.close()

def fn_add_timesheet_logs(called_function_arguments_dict):

    cursor = conn.cursor()
    action_ids_str = called_function_arguments_dict.get('action_ids', '')

    # If ids are not provided, just return
    if not action_ids_str:
        print("No ids provided to log against.")
        return

    # Split the id string by underscore (_) to get a list of ids
    action_id_strs = action_ids_str.split('_')

    # Convert each id string into an integer
    action_ids = [int(action_id_str) for action_id_str in action_id_strs]

    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)

    # Calculate the date 3 days ago
    three_days_ago = (datetime.datetime.now(tz) - datetime.timedelta(days=3)).strftime('%Y-%m-%d')

    sql = "INSERT INTO timesheets (action_id, date) VALUES (%s, %s)"

    # For each action_id, insert a new record only if it doesn't exist for the given date
    for action_id in action_ids:
        # Create a new cursor for this check
        check_cursor = conn.cursor()

        # Check if the action_id exists in actions table
        check_cursor.execute(f"SELECT * FROM actions WHERE id = {action_id}")
        if check_cursor.fetchone() is None:
            print(colored(f"action_id {action_id} does not exist in actions table. Skipping.", 'red'))
            continue

        # Check if action_id already has a log for the current date
        check_cursor.execute(f"SELECT * FROM timesheets WHERE action_id = {action_id} AND date = '{date}'")
        if check_cursor.fetchone() is None:
            values = (action_id, date)

            # Execute the command
            cursor.execute(sql, values)
        else:
            print(colored(f"Action_id: {action_id} already has an entry for date: {date}. Skipping.", 'cyan'))

        # Make sure to fetch all results before closing the cursor
        while check_cursor.fetchone() is not None:
            pass

        # Close the check cursor
        check_cursor.close()


    # Commit the transaction
    conn.commit()

    # Query the newly inserted rows
    cursor.execute(f"SELECT * FROM timesheets WHERE date = '{date}'")

    # Fetch all columns of the newly inserted rows
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]


    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    header_prefix = "TODAY'S" if date == default_date else f"{date}'s"

    # print()
    # print(colored(f"{header_prefix} TIMESHEET UPDATED", 'cyan'))
    # print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    print()

    # Query the actions that have been logged today
    cursor.execute(f"SELECT * FROM actions WHERE is_active = 1 AND id IN (SELECT action_id FROM timesheets WHERE date = '{date}') ORDER BY goal_id, deadline")
    actions_logged = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    print(colored(f"{header_prefix} ACTIONS", 'cyan'))
    if actions_logged:
        df_logged = pd.DataFrame(actions_logged, columns=column_names)
        print(colored(tabulate(df_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
        print()
    else:
        print()
        print(colored('YOU ARE ALIVE! \nGIVE GOD A FUCKING CRAZY PRAISE, \nAND GET STARTED NOW! BOOM! BOOM! BOOM! KABOOOM!', 'red'))
        print()


    # Query the actions that have not been logged today
    cursor.execute(f"SELECT * FROM actions WHERE is_active = 1 AND id NOT IN (SELECT action_id FROM timesheets WHERE date = '{date}') ORDER BY goal_id, deadline")
    actions_not_logged = cursor.fetchall()

    print(colored(f"{header_prefix} ACTIONABLES", 'cyan'))
    if actions_not_logged:
        df_not_logged = pd.DataFrame(actions_not_logged, columns=column_names)
        print(colored(tabulate(df_not_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('All actions have been logged today.')

    # Query the neglected actions
    cursor.execute(f"""
        SELECT * FROM actions
        WHERE is_active = 1 AND 
        id NOT IN (SELECT action_id FROM timesheets WHERE date > '{three_days_ago}' AND date <= '{date}')
        ORDER BY goal_id, deadline
    """)
    neglected_actions = cursor.fetchall()

    print()
    print(colored(f"{header_prefix} NEGLECTED ACTIONS (NO LOGS IN PRECEDING 3 DAYS)", 'cyan'))
    if neglected_actions:
        df_neglected = pd.DataFrame(neglected_actions, columns=column_names)
        print(colored(tabulate(df_neglected, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('No neglected actions.')

    cursor.close()
    conn.close()

def fn_list_timesheet_logs(called_function_arguments_dict):
    cursor = conn.cursor()

    # Get current date
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)

    # Calculate the date 3 days ago
    three_days_ago = (datetime.datetime.now(tz) - datetime.timedelta(days=3)).strftime('%Y-%m-%d')

    # Query the actions that have been logged today
    cursor.execute(
        f"SELECT * FROM actions WHERE is_active = 1 AND id IN (SELECT action_id FROM timesheets WHERE date = '{date}') ORDER BY goal_id, deadline")
    actions_logged = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    # Use 'TODAY' in the header if the date is today; otherwise, use the actual date
    header_prefix = "TODAY'S" if date == default_date else f"{date}'s"

    print()
    print(colored(f"{header_prefix} TIMESHEET:", 'cyan'))
    if actions_logged:
        df_logged = pd.DataFrame(actions_logged, columns=column_names)
        print(colored(tabulate(df_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
        print()
    else:
        print()
        print(colored('YOU ARE ALIVE! \nGIVE GOD A FUCKING CRAZY PRAISE, \nAND GET STARTED NOW! BOOM! BOOM! BOOM! KABOOOM!', 'red'))
        print()

    # Query the actions that have not been logged today
    cursor.execute(f"""
        SELECT * FROM actions
        WHERE is_active = 1 AND 
        id NOT IN (SELECT action_id FROM timesheets WHERE date = '{date}')
        ORDER BY goal_id, deadline
    """)
    actions_not_logged = cursor.fetchall()

    print(colored(f"{header_prefix} ACTIONABLES", 'cyan'))
    if actions_not_logged:
        df_not_logged = pd.DataFrame(actions_not_logged, columns=column_names)
        print(colored(tabulate(df_not_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('All actions have been logged today.')

    # Query the neglected actions
    cursor.execute(f"""
        SELECT * FROM actions
        WHERE is_active = 1 AND 
        id NOT IN (SELECT action_id FROM timesheets WHERE date > '{three_days_ago}' AND date <= '{date}')
        ORDER BY goal_id, deadline
    """)
    neglected_actions = cursor.fetchall()

    print()
    print(colored(f"{header_prefix} NEGLECTED ACTIONS (NO LOGS IN PRECEDING 3 DAYS)", 'cyan'))
    if neglected_actions:
        df_neglected = pd.DataFrame(neglected_actions, columns=column_names)
        print(colored(tabulate(df_neglected, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('No neglected actions.')

    cursor.close()
    conn.close()

def fn_delete_timesheet_logs(called_function_arguments_dict):

    cursor = conn.cursor()
    action_ids_str = called_function_arguments_dict.get('action_ids', '')
    three_days_ago = (datetime.datetime.now(tz) - datetime.timedelta(days=3)).strftime('%Y-%m-%d')

    # If ids are not provided, raise an error
    if not action_ids_str:
        raise ValueError("No ids provided to delete logs.")

    # Split the id string by underscore (_) to get a list of ids
    action_id_strs = action_ids_str.split('_')

    # Convert each id string into an integer
    action_ids = [int(action_id_str) for action_id_str in action_id_strs]

    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)

    sql = "DELETE FROM timesheets WHERE action_id = %s AND date = %s"

    # For each action_id, delete the record if it exists for the given date
    for action_id in action_ids:

        # Check if action_id has a log for the current date
        cursor.execute(f"SELECT * FROM timesheets WHERE action_id = {action_id} AND date = '{date}'")
        if cursor.fetchone() is not None:
            values = (action_id, date)

            # Execute the command
            cursor.execute(sql, values)
        else:
            print(colored(f"Action_id: {action_id} does not have an entry for date: {date}. Skipping.", 'cyan'))

    # Commit the transaction
    conn.commit()

    # Query the deleted rows
    cursor.execute(f"SELECT * FROM timesheets WHERE date = '{date}'")

    # Fetch all columns of the remaining rows after deletion
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    header_prefix = "TODAY'S" if date == default_date else f"{date}'s"
    print()

    cursor.execute(f"SELECT * FROM actions WHERE is_active = 1 AND id IN (SELECT action_id FROM timesheets WHERE date = '{date}') ORDER BY goal_id, deadline")
    actions_logged = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    print(colored(f"{header_prefix} ACTIONS", 'cyan'))
    if actions_logged:
        df_logged = pd.DataFrame(actions_logged, columns=column_names)
        print(colored(tabulate(df_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
        print()
    else:
        print()
        print(colored('YOU ARE ALIVE! \nGIVE GOD A FUCKING CRAZY PRAISE, \nAND GET STARTED NOW! BOOM! BOOM! BOOM! KABOOOM!', 'red'))
        print()

    # Query the actions that have not been logged today
    cursor.execute(f"SELECT * FROM actions WHERE is_active = 1 AND id NOT IN (SELECT action_id FROM timesheets WHERE date = '{date}') ORDER BY goal_id, deadline")
    actions_not_logged = cursor.fetchall()

    print(colored(f"{header_prefix} ACTIONABLES", 'cyan'))
    if actions_not_logged:
        df_not_logged = pd.DataFrame(actions_not_logged, columns=column_names)
        print(colored(tabulate(df_not_logged, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('All actions have been logged today.')

    # Query the neglected actions
    cursor.execute(f"""
        SELECT * FROM actions
        WHERE is_active = 1 AND 
        id NOT IN (SELECT action_id FROM timesheets WHERE date > '{three_days_ago}' AND date <= '{date}')
        ORDER BY goal_id, deadline
    """)
    neglected_actions = cursor.fetchall()

    print()
    print(colored(f"{header_prefix} NEGLECTED ACTIONS (NO LOGS IN PRECEDING 3 DAYS)", 'cyan'))
    if neglected_actions:
        df_neglected = pd.DataFrame(neglected_actions, columns=column_names)
        print(colored(tabulate(df_neglected, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print('No neglected actions.')

    cursor.close()
    conn.close()

def fn_display_timesheets_line_chart(called_function_arguments_dict):
    # Extract the upper_limit_days and lower_limit_days from the argument dict, with default values
    cursor = conn.cursor(dictionary=True)

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    days_ago_start = int(called_function_arguments_dict.get('days_ago_start',30))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))

    is_cumulative = called_function_arguments_dict.get('is_cumulative')

    start_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

    query = f"SELECT DATE(date) as date, COUNT(*) as total_entries FROM timesheets WHERE DATE(date) >= '{start_date}' AND DATE(date) <= '{end_date}' GROUP BY DATE(date) ORDER BY DATE(date)"
    # print(query)
    cursor.execute(query)
    timesheet_counts = cursor.fetchall()
    # print(timesheet_counts)

    if not timesheet_counts:
        print("No timesheet entries found in the specified date range.")
        return

    try:
        values = [entry['total_entries'] for entry in timesheet_counts]
    except ValueError as e:
        print(f"Error getting total_entries: {e}")
        return

    heading = f"TIMESHEET ENTRIES FROM {start_date} TO {end_date}"
    if is_cumulative != "false":
        values = [sum(values[:i + 1]) for i in range(len(values))]
        heading = f"CUMULATIVE TIMESHEET ENTRIES FROM {start_date} TO {end_date}"

    # Create chart
    plt.clc()  # clear previous plot
    plt.plotsize(70, 20)
    plt.ticks_color('red')
    plt.plot(values, color="red")
    plt.title(heading)
    plt.show()



    # Close the cursor and connection
    cursor.close()
    conn.close()


