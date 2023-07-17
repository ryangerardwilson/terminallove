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
            created_at = updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_cmd, ( '', is_published, created_at, updated_at))
            conn.commit()
            new_id = cursor.lastrowid
            created_at_filename = updated_at_filename = datetime.datetime.now().strftime('[C:%Y%m%d(%H%M%S)]')
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
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')

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

            # Get the modified time of the file
            mod_time = os.path.getmtime(file_path)
            # Convert it to a datetime object
            mod_time = datetime.datetime.fromtimestamp(mod_time)

            # Get the updated_at time from the database for the current note_id
            select_cmd = (
                "SELECT updated_at FROM notes WHERE id = %s"
            )
            cursor.execute(select_cmd, (note_id,))
            db_updated_at, = cursor.fetchone()  # Unpack the tuple here

            # Only perform the update if the file's modified time is newer than the db_updated_at time
            if mod_time > db_updated_at:
                update_cmd = (
                    "UPDATE notes SET note = %s, updated_at = %s WHERE id = %s"
                )
                updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(update_cmd, (note_content, updated_at, note_id))

            os.remove(file_path)
            print(colored(f"Saved and closed note at: {file_path}",'cyan'))
            is_any_file_saved = True

    conn.commit()
    cursor.close()

    if is_any_file_saved:
        print(colored('Notes saved to database', 'cyan'))
    else:
        print(colored('No notes to save', 'cyan'))

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
        sql = "DELETE FROM notes WHERE id = %s"
        cursor.execute(sql, (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    print(colored(f"NOTES WITH IDS {ids_to_delete} DELETED", 'cyan'))
