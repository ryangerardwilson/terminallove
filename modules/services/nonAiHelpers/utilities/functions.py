import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt
import sys
import subprocess
import re

pd.set_option('display.precision', 10)

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
load_dotenv(os.path.join(parent_dir, '.env'))

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)



def fn_display_passwords():

    cursor = conn.cursor()

    # SQL query to retrieve passwords (assuming your table is called 'passwords_table')
    query = "SELECT * FROM passwords"

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Extract the column names
    column_names = [column[0] for column in cursor.description]

    # Print the passwords in tabular form
    print()
    print(colored('PASSWORDS TABLE', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

    # Close the cursor and the connection
    cursor.close()
    conn.close()


def fn_display_functionalities():
    utilities = [
        {
            "command": "--update",
            "description": "pulls the lastest version of the bot from the git repo",
        },
        {
            "command": "--p",
            "description": "displays passwords",
        },
        {
            "command": "--p:create",
            "description": "create password",
        },
        {
            "command": "--p:update",
            "description": "update password",
        },
        {
            "command": "--p:delete",
            "description": "delete password",
        },
        {
            "command": "--l",
            "description": "lists all functionalities",
        },
        {
            "command": "--m",
            "description": "displays all metrics charts",
        },
        {
            "command": "--reset",
            "description": "clears history of AI chat",
        },

        {
            "command": "--db",
            "description": "displays credentials from the mysql_databases table",
        },
        {
            "command": "--db --id n",
            "description": "mysql connect to a mysql database with id n in the mysql_databases table",
        },
        {
            "command": "--db:schema --id n",
            "description": "prints the schema of all tables of a mysql database with id n in the mysql_databases table",
        },
        {
            "command": "--db:create",
            "description": "displays syntax to create a record in the mysql_databases table",
        },
        {
            "command": "--db:update",
            "description": "displays syntax to update a record in the mysql_databases table",
        },
        {
            "command": "--db:delete",
            "description": "displays syntax to delete a record in the mysql_databases table",
        },
        {
            "command": "--vm",
            "description": "displays credentials from virtual_machines table",
        },
        {
            "command": "--vm --id n",
            "description": "ssh into a virtual machine with id n in the virtual_machines table",
        },
        {
            "command": "--vm:create",
            "description": "displays syntax to create a record in the virtual_machines table",
        },
        {
            "command": "--vm:update",
            "description": "displays syntax to update a record in the virtual_machines table",
        },
        {
            "command": "--vm:delete",
            "description": "displays syntax to delete a record in the virtual_machines table",
        },

        # Add more entries here, each as a separate dictionary
    ]

    # Convert the passwords to a list of lists
    rows = [
        [index + 1, entry["command"], entry["description"]]
        for index, entry in enumerate(utilities)
    ]

    # Column names
    column_names = ["", "command", "description"]

    # Print the passwords in tabular form
    print()
    print(colored('UTILITY COMMANDS', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()


def fn_create_password(service, username, password, comments):
    cursor = conn.cursor()
    # SQL query to insert a new record into the passwords table
    query = """
        INSERT INTO passwords (service, username, password, comments)
        VALUES (%s, %s, %s, %s);
    """

    # Execute the query
    cursor.execute(query, (service, username, password, comments))
    # Commit the transaction
    conn.commit()
    print(colored("Password record created successfully.", 'cyan'))


def fn_update_password(id, service, username, password, comments):
    cursor = conn.cursor()

    # Initialize query and parameters
    query = "UPDATE passwords SET"
    params = []

    # Append service if not empty
    if service:
        query += " service = %s,"
        params.append(service)

    # Append username if not empty
    if username:
        query += " username = %s,"
        params.append(username)

    # Append password if not empty
    if password:
        query += " password = %s,"  # ensure the column name is correct
        params.append(password)

    # Append comments if not empty
    if comments != None:
        query += " comments = %s,"
        params.append(comments)

    # Remove trailing comma and add the WHERE clause
    query = query.rstrip(",") + " WHERE id = %s;"
    params.append(id)

    # Execute the query if there are updates to make
    if len(params) > 1:
        cursor.execute(query, params)
        conn.commit()
        print(colored("Password record updated successfully.", 'cyan'))
    else:
        print("No fields to update.")


def fn_delete_password(id):
    cursor = conn.cursor()
    # SQL query to delete a record from the passwords table
    query = """
        DELETE FROM passwords
        WHERE id = %s;
    """
    # Execute the query
    cursor.execute(query, (id,))
    # Commit the transaction
    conn.commit()
    print(colored("Password record deleted successfully.", 'cyan'))


def fn_display_vm_records():
    cursor = conn.cursor()

    # SQL query to retrieve passwords (assuming your table is called 'passwords_table')
    query = "SELECT * FROM virtual_machines"

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Extract the column names
    column_names = [column[0] for column in cursor.description]

    # Print the passwords in tabular form
    print()
    print(colored('SSH TABLE', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

def fn_create_vm_record(description, command, password):

    cursor = conn.cursor()
    # SQL query to insert a new record into the passwords table
    if password == None:
        query = """
            INSERT INTO virtual_machines (description, command)
            VALUES (%s, %s);
        """
        cursor.execute(query, (description, command))
    else:
        query = """
            INSERT INTO virtual_machines (description, command, password)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (description, command, password))

    # Execute the query

    # Commit the transaction
    conn.commit()
    print(colored("VM record created successfully.", 'cyan'))


def fn_update_vm_record(id, description, command, password):
    cursor = conn.cursor()

    # Initialize query and parameters
    query = "UPDATE virtual_machines SET"
    params = []

    # Append service if not empty
    if description:
        query += " description = %s,"
        params.append(description)

    # Append username if not empty
    if command:
        query += " command = %s,"
        params.append(command)

    if password != None:
        query += " password = %s,"
        params.append(password)


    # Remove trailing comma and add the WHERE clause
    query = query.rstrip(",") + " WHERE id = %s;"
    params.append(id)

    # Execute the query if there are updates to make
    if len(params) > 1:
        cursor.execute(query, params)
        conn.commit()
        print(colored("VM record updated successfully.", 'cyan'))
    else:
        print("No fields to update.")


def fn_delete_vm_record(id):
    cursor = conn.cursor()
    # SQL query to delete a record from the passwords table
    query = """
        DELETE FROM virtual_machines
        WHERE id = %s;
    """
    # Execute the query
    cursor.execute(query, (id,))
    # Commit the transaction
    conn.commit()
    print(colored("VM record deleted successfully.", 'cyan'))


def fn_ssh_into_vm(id):
    cursor = conn.cursor(dictionary=True)

    # SQL query to fetch the record from the ssh table
    query = """
        SELECT * FROM virtual_machines
        WHERE id = %s;
    """

    # Execute the query
    cursor.execute(query, (id,))
    # Fetch the record
    record = cursor.fetchone()

    # Check if the record exists
    if record:
        # Extract the SSH command
        ssh_command = record['command']
        password = record['password']

        # Replace the key in the SSH command with the absolute path
        key_relative_path = "files/ssh/"

        # Use regular expression to find the -i key_filename pattern
        match = re.search(r'-i (\S+)', ssh_command)
        if match:
            key_filename = match.group(1)
            key_absolute_path = os.path.join(parent_dir, key_relative_path, key_filename)
            ssh_command = ssh_command.replace(key_filename, key_absolute_path)

        # Print the SSH command (Caution: This could be a security risk if it contains sensitive information)
        print()
        print(colored(f"Executing VM SSH command: {ssh_command}", 'cyan'))
        print(colored(f"Password: {password}", 'red'))
        print()

        # Execute the SSH command
        try:
            subprocess.run(ssh_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(colored(f"VM SSH command failed: {str(e)}", 'red'))
        except Exception as e:
            print(colored(f"An error occurred: {str(e)}", 'red'))
    else:
        print(colored("VM record not found.", 'red'))

    cursor.close()






def fn_display_db_records():
    cursor = conn.cursor()

    # SQL query to retrieve passwords (assuming your table is called 'passwords_table')
    query = "SELECT * FROM mysql_databases"

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Extract the column names
    column_names = [column[0] for column in cursor.description]

    # Print the passwords in tabular form
    print()
    print(colored('MYSQL DATABASES TABLE', 'red'))
    print()
    print(colored(tabulate(rows, headers=column_names), 'cyan'))
    print()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

def fn_create_db_record(description, command, password):

    cursor = conn.cursor()
    # SQL query to insert a new record into the passwords table
    if password == None:
        query = """
            INSERT INTO mysql_databases (description, command)
            VALUES (%s, %s);
        """
        cursor.execute(query, (description, command))
    else:
        query = """
            INSERT INTO mysql_databases (description, command, password)
            VALUES (%s, %s, %s);
        """
        cursor.execute(query, (description, command, password))

    # Execute the query

    # Commit the transaction
    conn.commit()
    print(colored("MYSQL DB record created successfully.", 'cyan'))


def fn_update_db_record(id, description, command, password):
    cursor = conn.cursor()

    # Initialize query and parameters
    query = "UPDATE mysql_databases SET"
    params = []

    # Append service if not empty
    if description:
        query += " description = %s,"
        params.append(description)

    # Append username if not empty
    if command:
        query += " command = %s,"
        params.append(command)

    if password != None:
        query += " password = %s,"
        params.append(password)


    # Remove trailing comma and add the WHERE clause
    query = query.rstrip(",") + " WHERE id = %s;"
    params.append(id)

    # Execute the query if there are updates to make
    if len(params) > 1:
        cursor.execute(query, params)
        conn.commit()
        print(colored("MYSQL DB record updated successfully.", 'cyan'))
    else:
        print("No fields to update.")


def fn_delete_db_record(id):
    cursor = conn.cursor()
    # SQL query to delete a record from the passwords table
    query = """
        DELETE FROM mysql_databases
        WHERE id = %s;
    """
    # Execute the query
    cursor.execute(query, (id,))
    # Commit the transaction
    conn.commit()
    print(colored("MYSQL DB record deleted successfully.", 'cyan'))


def fn_mysql_connect_to_db(id):
    cursor = conn.cursor(dictionary=True)
    # SQL query to fetch the record from the ssh table
    query = """
        SELECT * FROM mysql_databases
        WHERE id = %s;
    """
    # Execute the query
    cursor.execute(query, (id,))
    # Fetch the record
    record = cursor.fetchone()

    # Check if the record exists
    if record:
        # Extract the SSH command
        ssh_command = record['command']
        password = record['password']

        # Print the SSH command (Caution: This could be a security risk if it contains sensitive information)
        print()
        print(colored(f"Executing MYSQL DB CONNECT command: {ssh_command}", 'cyan'))
        print(colored(f"Password: {password}", 'red'))
        print()

        # Execute the SSH command
        try:
            subprocess.run(ssh_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(colored(f"MYSQL DB CONNECT command failed: {str(e)}", 'red'))
        except Exception as e:
            print(colored(f"An error occurred: {str(e)}", 'red'))
    else:
        print(colored("MYSQL DB record not found.", 'red'))

    cursor.close()


def fn_display_db_schema(id):
    # Step 1 - get the database connection details from mysql_databases using id

    cursor = conn.cursor(dictionary=True)
    # SQL query to get database record by id
    query = """
        SELECT * FROM mysql_databases
        WHERE id = %s;
    """
    # Execute the query
    cursor.execute(query, (id,))
    # Fetch the result
    db_record = cursor.fetchone()
    if db_record is None:
        print("No database record found with the provided id")
        return

    # Retrieve the command (assuming it's stored in a column named 'command')
    command = db_record['command']

    # Parse command using regex to get username, password, and database name
    match = re.match(r'mysql -h "(.+)" -u "(.+)" -p"(.+)" "(.+)"', command)
    if match is None:
        print("Failed to parse the database connection command")
        return

    host, username, password, database_name = match.groups()

    # Step 2 - Connect to the database specified by the username, password, and database_name and display the schema of that database only

    # Close the initial cursor as it's not needed anymore
    cursor.close()

    # Establish a new connection to the specific database
    conn2 = mysql.connector.connect(
        host=host,
        user=username,
        passwd=password,
        database=database_name
    )

    # Retrieve the list of tables
    cursor2 = conn2.cursor(dictionary=True)
    cursor2.execute("SHOW TABLES")
    tables = cursor2.fetchall()

    # For each table, retrieve the schema and print it
    for table in tables:
        key = next(iter(table.keys()))
        table_name = table[key]
        print()
        print(colored(f"SCHEMA FOR TABLE: {table_name}", 'red'))
        print()


        # Retrieve the schema of the table
        cursor2.execute(f"DESCRIBE {table_name}")
        schema = cursor2.fetchall()

        # Extract the column names dynamically from the first row of the result
        column_names = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']

        # Convert the list of dictionaries to a list of lists
        schema_as_list = [[column[name] for name in column_names] for column in schema]

        # Print the schema in tabular form
        print(colored(tabulate(schema_as_list, headers=column_names), 'cyan'))

    print()

    # Close the cursor and the connection
    cursor2.close()
    conn2.close()
