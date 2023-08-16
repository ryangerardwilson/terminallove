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

def fn_list_runs_module_functions(called_function_arguments_dict):
    functions = [
            {
                "function": "list_run_logging_params",
                "description": "If user is confused, list the parameters required to log a run",
            },
            {
                "function": "add_run_logs",
                "description": "Adds/logs the user's run to the runs table",
            },
            {
                "function": "list_run_logs",
                "description": "Lists the user's runs",
            },
            {
                "function": "update_run_by_id",
                "description": "Update a run log by its id i.e. the run id",
            },
            {
                "function": "delete_runs_by_ids",
                "description": "Delete runs by their ids",
            },
            {
                "function": "list_available_running_charts",
                "description": "Lists the available running charts",
            },
            {
                "function": "display_running_weight_line_chart",
                "description": "Plots a line chart of the user's weight over the given range of days",
            },
            {
                "function": "display_runs_fat_burn_line_chart",
                "description": "Plots a line chart of the user's fat burn / zone 2 running minutes over the given range of days",
            },
            {
                "function": "display_runs_distance_line_chart",
                "description": "Plots a line chart of the user's distance covered while running over the given range of days",
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
    print(colored('RUNS MODULE FUNCTIONS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

def fn_list_run_logging_params(called_function_arguments_dict):
        print(colored('The following parameters are required:', 'cyan'))
        print(colored('1.  pre_run_weight_kgs', 'cyan'))
        print(colored('2.  post_run_weight_kgs', 'cyan'))
        print(colored('3.  fat_burn_zone_minutes', 'cyan'))
        print(colored('4.  cardio_zone_minutes', 'cyan'))
        print(colored('5.  peak_zone_minutes', 'cyan'))
        print(colored('6.  distance_covered_kms', 'cyan'))
        print(colored('7.  temperature', 'cyan'))
        print(colored('8.  date (default is today)', 'cyan'))



def fn_add_run_logs(called_function_arguments_dict):
    
    cursor = conn.cursor()

    # Set default values
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')

    pre_run_weight_lbs = called_function_arguments_dict.get('pre_run_weight_lbs', 0)
    post_run_weight_lbs = called_function_arguments_dict.get('post_run_weight_lbs', 0)
    fat_burn_zone_minutes = called_function_arguments_dict.get('fat_burn_zone_minutes', 0)
    cardio_zone_minutes = called_function_arguments_dict.get('cardio_zone_minutes', 0)
    peak_zone_minutes = called_function_arguments_dict.get('peak_zone_minutes', 0)
    distance_covered_kms = called_function_arguments_dict.get('distance_covered_kms', 0)
    temperature_in_f = called_function_arguments_dict.get('temperature_in_f', 0)
    date = called_function_arguments_dict.get('date', default_date)

    sql = "INSERT INTO runs (pre_run_weight_lbs, post_run_weight_lbs, fat_burn_zone_minutes, cardio_zone_minutes, peak_zone_minutes, distance_covered_kms, temperature_in_f, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (pre_run_weight_lbs, post_run_weight_lbs, fat_burn_zone_minutes, cardio_zone_minutes, peak_zone_minutes, distance_covered_kms, temperature_in_f, date)

    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute(f"SELECT * FROM runs WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    headers = ["pre-weight", "post-weight", "fat burn", "cardio", "peak", "distance", "date", "temp"]

    print(colored(tabulate(df, headers=headers, tablefmt='psql', showindex=False), 'cyan'))



def fn_list_run_logs(called_function_arguments_dict):
    cursor = conn.cursor()

    # Query to get all events sorted by date in descending order
    cursor.execute("SELECT * FROM runs ORDER BY date DESC")

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

    headers = ["pre-weight", "post-weight", "fat burn", "cardio", "peak", "distance", "date", "temp"]

    # Print the data
    print(colored(tabulate(df, headers=headers, tablefmt='psql', showindex=False), 'cyan'))


def fn_update_run_by_id(called_function_arguments_dict):

    run_id = called_function_arguments_dict.pop('run_id')

    cursor = conn.cursor()

    update_columns = []
    values = []

    for key, value in called_function_arguments_dict.items():
        if value is not None:
            update_columns.append(f"{key} = %s")
            values.append(value)

    update_columns = ', '.join(update_columns)
    values.append(run_id)  # Add event_id to the end of values list

    sql = f"UPDATE runs SET {update_columns} WHERE id = %s"

    cursor.execute(sql, values)

    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM runs WHERE id = {run_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    df = pd.DataFrame(result)

    cursor.close()
    conn.close()

    headers = ["pre-weight", "post-weight", "fat burn", "cardio", "peak", "distance", "date", "temp"]

    print(colored(f"Run with id {run_id} updated successfully.", 'cyan'))
    print(colored(tabulate(df, headers=headers, tablefmt='psql', showindex=False), 'cyan'))



def fn_delete_runs_by_ids(called_function_arguments_dict):
    cursor = conn.cursor()

    ids_to_delete = called_function_arguments_dict.get('ids').split('_')

    for id in ids_to_delete:
        sql = "DELETE FROM runs WHERE id = %s"
        cursor.execute(sql, (id,))

    conn.commit()

    cursor.close()
    conn.close()

    print(colored(f"Runs with ids {ids_to_delete} deleted successfully.", 'cyan'))

def fn_list_available_running_charts(called_function_arguments_dict):
    print(colored('1.  Running Weight Chart (optional - range of days)', 'cyan'))
    print(colored('2.  Running Fat Burn Chart (optional - range of days, is cumulative)', 'cyan'))
    print(colored('3.  Running Distance Chart (optional - range of days, is cumulative)', 'cyan'))

def fn_display_running_weight_line_chart(called_function_arguments_dict):
    cursor = conn.cursor(dictionary=True)

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    days_ago_start = int(called_function_arguments_dict.get('days_ago_start', 30))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))
    start_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

   # Modify the query to calculate average weights
    query = """
        SELECT DATE(date) as date, AVG(pre_run_weight_lbs) as avg_pre_run_weight, AVG(post_run_weight_lbs) as avg_post_run_weight
        FROM runs
        WHERE DATE(date) >= %s AND DATE(date) <= %s
        GROUP BY DATE(date)
        ORDER BY DATE(date)
    """

    # Execute the query
    cursor.execute(query, (start_date, end_date))
    
    runs = cursor.fetchall()

    if not runs:
        print("No runs found in the specified date range.")
        return

    try:
        pre_run_values = [float(run['avg_pre_run_weight']) for run in runs]
        post_run_values = [float(run['avg_post_run_weight']) for run in runs]
        dates = [run['date'] for run in runs]
    except ValueError as e:
        print(f"Error converting total_value to float: {e}")
        return

    heading = f"AVERAGE PRE-RUN AND POST-RUN WEIGHT FROM {start_date} TO {end_date}"
    x_indices = range(len(dates))
    plt.clc()  # clear previous plot
    # Plot the pre_run_weights
    plt.plot(x_indices, pre_run_values, label="Average Pre-run Weight (kgs)", color="red")

    # Plot the post_run_weights
    plt.plot(x_indices, post_run_values, label="Average Post-run Weight (kgs)", color="cyan")

    # Add title and labels
    plt.plotsize(70, 20)
    plt.title(heading)
    plt.xlabel("Date")
    plt.ylabel("Weight (kgs)")

    print()
    # Show the plot
    plt.show()


def fn_display_runs_fat_burn_line_chart(called_function_arguments_dict):

    cursor = conn.cursor(dictionary=True)

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    days_ago_start = int(called_function_arguments_dict.get('days_ago_start', 30))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))
    start_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

    is_cumulative = called_function_arguments_dict.get('is_cumulative')

    # Include all expenses
    query = "SELECT DATE(date) as date, SUM(fat_burn_zone_minutes) as total_value FROM runs WHERE DATE(date) >= %s AND DATE(date) <= %s GROUP BY DATE(date) ORDER BY DATE(date)"


    # cursor.execute(query)
    cursor.execute(query, (start_date, end_date))
     

    runs = cursor.fetchall()

    if not runs:
        print("No runs found in the specified date range.")
        return

    try:
        values = [float(run['total_value']) for run in runs]

    except ValueError as e:
        print(f"Error converting total_value to float: {e}")
        return

    heading = f"FAT BURN RUNNING MINUTES FROM {start_date} TO {end_date}"
    if is_cumulative != "false":
        values = [sum(values[:i + 1]) for i in range(len(values))]
        heading = f"CUMULATIVE FAT BURN RUNNING MINUTES FROM {start_date} TO {end_date}"

    plt.clc()  # clear previous plot
    plt.plot(values, color="red")
    plt.plotsize(70, 20)
    plt.title(heading)
    print()
    plt.show()

    cursor.close()
    conn.close()


def fn_display_runs_distance_line_chart(called_function_arguments_dict):
    cursor = conn.cursor(dictionary=True)

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    days_ago_start = int(called_function_arguments_dict.get('days_ago_start', 30))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))
    start_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now(tz) - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

    is_cumulative = called_function_arguments_dict.get('is_cumulative')

    # Query to sum distance_covered_kms grouped by date
    query = "SELECT DATE(date) as date, SUM(distance_covered_kms) as total_distance FROM runs WHERE DATE(date) >= %s AND DATE(date) <= %s GROUP BY DATE(date) ORDER BY DATE(date)"

    # Execute query
    cursor.execute(query, (start_date, end_date))

    # Fetch runs
    runs = cursor.fetchall()

    if not runs:
        print("No runs found in the specified date range.")
        return

    try:
        values = [float(run['total_distance']) for run in runs]
    except ValueError as e:
        print(f"Error converting total_distance to float: {e}")
        return

    heading = f"DISTANCE COVERED IN KMS FROM {start_date} TO {end_date}"
    if is_cumulative != "false":
        values = [sum(values[:i + 1]) for i in range(len(values))]
        heading = f"CUMULATIVE DISTANCE COVERED IN KMS FROM {start_date} TO {end_date}"

    # Plot the distances
    plt.clc()  # clear previous plot
    plt.plot(values, color="red")
    plt.plotsize(70, 20)
    plt.title(heading)
    print()
    plt.show()

    cursor.close()
    conn.close()
