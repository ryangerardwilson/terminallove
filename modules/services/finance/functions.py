import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt

pd.set_option('display.precision', 10)

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

PRIMARY_CREDIT_CARD_INTEREST_COEFFICIENT_AGAINST_NEW_EXPENSES = os.getenv('PRIMARY_CREDIT_CARD_INTEREST_COEFFICIENT_AGAINST_NEW_EXPENSES')
DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD = os.getenv('DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD')

def fn_list_expense_logging_params():
    print(colored('The following parameters are required:', 'cyan'))
    print(colored('1.  value', 'cyan'))
    print(colored('2.  expense_date', 'cyan'))
    print(colored('3.  currency (default is INR)', 'cyan'))
    print(colored('4.  particulars', 'cyan'))
    print(colored('5.  debt_id (optional integer linking to a debt record)', 'cyan'))
    print(colored('6.  is_debt_repayment (optional, boolean: 0 or 1, default is 0)', 'cyan'))
    print(colored('7.  is_earmarked_for_debt_repayment (optional, boolean: 0 or 1, default is 0)', 'cyan'))

def fn_log_expenses(called_function_arguments_dict):

    cursor = conn.cursor()

    # Set default values
    default_currency = 'INR'
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # If "currency" and "expense_date" are not in called_function_arguments_dict, set them to the defaults
    currency = called_function_arguments_dict.get('currency', default_currency)
    particulars = called_function_arguments_dict.get('particulars')
    expense_date_str = called_function_arguments_dict.get('expense_date', default_date)


    # Convert "value" to float as it's a string in the dictionary
    value = float(called_function_arguments_dict['value'])

    debt_id = int(called_function_arguments_dict.get('debt_id', DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD))
    is_debt_repayment_str = called_function_arguments_dict.get('is_debt_repayment')

    if is_debt_repayment_str == "true":
        is_debt_repayment = 1
        debt_id = called_function_arguments_dict.get('debt_id', DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD)

    is_earmarked_for_debt_repayment = 0
    is_debt_repayment = 0

    sql = "INSERT INTO expenses (value, particulars, expense_date, currency, debt_id, is_debt_repayment, is_earmarked_for_debt_repayment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (value, particulars, expense_date_str, currency, debt_id, is_debt_repayment, is_earmarked_for_debt_repayment)
    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute("SELECT * FROM expenses WHERE id = %s", (last_id,))

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    df['value'] = df['value'].astype(int)

    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    if debt_id != 0:

        # Selecting all the debt_ids from debts table
        cursor.execute("SELECT id FROM debts")
        debt_ids = [row[0] for row in cursor.fetchall()]

        # Iterating through each debt_id
        for debt_id_instance in debt_ids:
            # Fetch the most recent log of the corresponding debt_id
            cursor.execute("SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id_instance,))
            most_recent_log_date = cursor.fetchone()[0]

            # If most_recent_log_date is None, continue to next iteration
            if most_recent_log_date is None:
                continue

            # Fetch the total_amount and outstanding on most_recent_log_date
            cursor.execute("""
                SELECT total_amount, outstanding
                FROM debt_status_logs
                WHERE debt_id = %s AND status_date = %s
            """, (debt_id_instance, most_recent_log_date))
            initial_total_amount, initial_outstanding = cursor.fetchone()

            # Fetch the sum of relevant expenses for the current debt_id
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN is_debt_repayment = true THEN -value ELSE value END),
                    COUNT(*)
                FROM expenses 
                WHERE debt_id = %s AND expense_date > %s
            """, (debt_id_instance, most_recent_log_date))

            total_value, count = cursor.fetchone()

            # If there are no relevant expenses, continue to next iteration
            if count == 0:
                continue

            # Update total_amount and outstanding in the debts table
            if int(debt_id_instance) == int(DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD):
                new_total_amount = initial_total_amount + total_value
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))
            else:
                new_total_amount = initial_total_amount
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))

        # Committing the changes to the database
        conn.commit()

        cursor.execute(f"SELECT * FROM debts WHERE id = {debt_id}")
        columns = cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
        debts_df = pd.DataFrame(result)
        debts_df['total_amount'] = debts_df['total_amount'].astype(int)
        debts_df['outstanding'] = debts_df['outstanding'].astype(int)
        print()
        print(colored('IMPACTED DEBTS', 'cyan'))
        print(colored(f"Debt with id {debt_id} updated successfully.", 'cyan'))
        print(colored(tabulate(debts_df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

        cursor.close()
        conn.close()

def fn_log_debt_repayment(called_function_arguments_dict):

    cursor = conn.cursor()

    # Set default values
    default_currency = 'INR'
    default_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # If "currency" and "expense_date" are not in called_function_arguments_dict, set them to the defaults
    currency = called_function_arguments_dict.get('currency', default_currency)
    # particulars = called_function_arguments_dict.get('particulars')
    expense_date_str = called_function_arguments_dict.get('expense_date', default_date)

    # Convert expense_date_str to a datetime.date object
    # expense_date = datetime.datetime.strptime(expense_date_str, '%Y-%m-%d').date()

    # Convert "value" to float as it's a string in the dictionary
    value = float(called_function_arguments_dict['value'])

    is_debt_repayment = 1
    debt_id = called_function_arguments_dict.get('debt_id', DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD)

    # Fetch the source of the debt repayment
    cursor.execute("SELECT source FROM debts WHERE id = %s", (debt_id,))
    source = cursor.fetchone()[0]
    particulars = f"Repayment of {source}"

    is_earmarked_for_debt_repayment_str = called_function_arguments_dict.get('is_earmarked')
    is_earmarked_for_debt_repayment = 0
    if is_earmarked_for_debt_repayment_str != "false":
        is_earmarked_for_debt_repayment = 1
        is_debt_repayment = 0

    sql = "INSERT INTO expenses (value, particulars, expense_date, currency, debt_id, is_debt_repayment, is_earmarked_for_debt_repayment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (value, particulars, expense_date_str, currency, debt_id, is_debt_repayment, is_earmarked_for_debt_repayment)
    # Execute the command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row
    last_id = cursor.lastrowid

    # Query the last inserted row
    cursor.execute("SELECT * FROM expenses WHERE id = %s", (last_id,))

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    df['value'] = df['value'].astype(int)

    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    if debt_id != 0:

        # Selecting all the debt_ids from debts table
        cursor.execute("SELECT id FROM debts")
        debt_ids = [row[0] for row in cursor.fetchall()]

        # Iterating through each debt_id
        for debt_id_instance in debt_ids:
            # Fetch the most recent log of the corresponding debt_id
            cursor.execute("SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id_instance,))
            most_recent_log_date = cursor.fetchone()[0]

            # If most_recent_log_date is None, continue to next iteration
            if most_recent_log_date is None:
                continue

            # Fetch the total_amount and outstanding on most_recent_log_date
            cursor.execute("""
                SELECT total_amount, outstanding
                FROM debt_status_logs
                WHERE debt_id = %s AND status_date = %s
            """, (debt_id_instance, most_recent_log_date))
            initial_total_amount, initial_outstanding = cursor.fetchone()

            # Fetch the sum of relevant expenses for the current debt_id
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN is_debt_repayment = true THEN -value ELSE value END),
                    COUNT(*)
                FROM expenses 
                WHERE debt_id = %s AND expense_date > %s
            """, (debt_id_instance, most_recent_log_date))

            total_value, count = cursor.fetchone()

            # If there are no relevant expenses, continue to next iteration
            if count == 0:
                continue

            # Update total_amount and outstanding in the debts table
            if int(debt_id_instance) == int(DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD):
                new_total_amount = initial_total_amount + total_value
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))
            else:
                new_total_amount = initial_total_amount
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))

        # Committing the changes to the database
        conn.commit()

        cursor.execute(f"SELECT * FROM debts WHERE id = {debt_id}")
        columns = cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
        debts_df = pd.DataFrame(result)
        debts_df['total_amount'] = debts_df['total_amount'].astype(int)
        debts_df['outstanding'] = debts_df['outstanding'].astype(int)
        print()
        print(colored('IMPACTED DEBTS', 'cyan'))
        print(colored(f"Debt with id {debt_id} updated successfully.", 'cyan'))
        print(colored(tabulate(debts_df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

        cursor.close()
        conn.close()

def fn_list_expenses(called_function_arguments_dict):

    cursor = conn.cursor()

    now = datetime.datetime.now()
    start_of_month = datetime.datetime(now.year, now.month, 1)

    # Calculate the number of days since the start of the month
    days_since_start_of_month = (now - start_of_month).days

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    if called_function_arguments_dict.get('days_ago_start') is None:
        days_ago_start = days_since_start_of_month
    else:
        days_ago_start = int(called_function_arguments_dict.get('days_ago_start', days_since_start_of_month))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))

    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

    include_debt_repayment_str = called_function_arguments_dict.get('include_debt_repayment', 'true')
    if include_debt_repayment_str == "true":
        query = "SELECT * FROM expenses WHERE DATE(expense_date) >= %s AND DATE(expense_date) <= %s ORDER BY expense_date DESC"
        heading = f"EXPENSES (INCLUDING DEBT REPAYMENTS) FROM {start_date} TO {end_date}"
    else:
        query = "SELECT * FROM expenses WHERE is_debt_repayment = 0 AND is_earmarked_for_debt_repayment = 0 AND DATE(expense_date) >= %s AND DATE(expense_date) <= %s ORDER BY expense_date DESC"
        heading = f"EXPENSES (EXCLUDING DEBT REPAYMENTS) FROM {start_date} TO {end_date}"

    cursor.execute(query, (start_date, end_date))

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    if 'value' in df.columns:
        df['value'] = df['value'].astype(int)


    # Close the cursor and connection
    cursor.close()
    conn.close()

    headers = ['id', 'value', 'date', 'currency', 'particulars', 'debt_id', 'repays debt', 'earmarked to repay debt']

    # Print the data
    print()
    print(colored(heading, 'cyan'))
    print(colored(tabulate(df, headers=headers, tablefmt='psql', showindex=False), 'cyan'))

def fn_update_expense_by_id(called_function_arguments_dict):
    # Extract the id from the argument dictionary
    expense_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    # Convert "value" to float if it's a string in the dictionary and it's present
    if 'value' in called_function_arguments_dict:
        called_function_arguments_dict['value'] = float(called_function_arguments_dict['value'])

    if 'repaid_debt_id' in called_function_arguments_dict:
        called_function_arguments_dict['repaid_debt_id'] = int(called_function_arguments_dict['repaid_debt_id'])

    if 'is_debt_repayment' in called_function_arguments_dict:
        is_earmarked_for_debt_repayment_str = called_function_arguments_dict.get('is_debt_repayment')
        called_function_arguments_dict['is_debt_repayment'] = 0
        if is_earmarked_for_debt_repayment_str != "false":
            called_function_arguments_dict['is_debt_repayment'] = 1

    if 'is_earmarked_for_debt_repayment' in called_function_arguments_dict:
        is_earmarked_for_debt_repayment_str = called_function_arguments_dict.get('is_earmarked_for_debt_repayment')
        called_function_arguments_dict['is_earmarked_for_debt_repayment'] = 0
        if is_earmarked_for_debt_repayment_str != "false":
            called_function_arguments_dict['is_earmarked_for_debt_repayment'] = 1
            called_function_arguments_dict['is_debt_repayment'] = 0

    # Prepare the update query
    update_statements = ', '.join(f'{key} = %s' for key in called_function_arguments_dict.keys())
    sql = f"UPDATE expenses SET {update_statements} WHERE id = %s"

    # Add the id to the end of the values list for the WHERE clause in the SQL query
    values = tuple(called_function_arguments_dict.values()) + (expense_id,)

    # Execute the UPDATE command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    cursor.execute(f"SELECT debt_id FROM expenses WHERE id = {expense_id}")
    committed_debt_id = cursor.fetchone()[0]

    debts_df = pd.DataFrame()
    if 'value' in called_function_arguments_dict and committed_debt_id != 0:

        cursor.execute("SELECT id FROM debts")
        debt_ids = [row[0] for row in cursor.fetchall()]

        for debt_id_instance in debt_ids:
            # Fetch the most recent log of the corresponding debt_id
            cursor.execute("SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id_instance,))
            most_recent_log_date = cursor.fetchone()[0]

            # If most_recent_log_date is None, continue to next iteration
            if most_recent_log_date is None:
                continue

            # Fetch the total_amount and outstanding on most_recent_log_date
            cursor.execute("""
                SELECT total_amount, outstanding
                FROM debt_status_logs
                WHERE debt_id = %s AND status_date = %s
            """, (debt_id_instance, most_recent_log_date))
            initial_total_amount, initial_outstanding = cursor.fetchone()

            # Fetch the sum of relevant expenses for the current debt_id
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN is_debt_repayment = true THEN -value ELSE value END),
                    COUNT(*)
                FROM expenses 
                WHERE debt_id = %s AND expense_date > %s
            """, (debt_id_instance, most_recent_log_date))

            total_value, count = cursor.fetchone()

            # If there are no relevant expenses, continue to next iteration
            if count == 0:
                continue

            # Update total_amount and outstanding in the debts table
            if int(debt_id_instance) == int(DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD):
                new_total_amount = initial_total_amount + total_value
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))
            else:
                new_total_amount = initial_total_amount
                new_outstanding = initial_outstanding + total_value
                cursor.execute("""
                            UPDATE debts 
                            SET total_amount = %s,
                                outstanding = %s
                            WHERE id = %s
                        """, (new_total_amount, new_outstanding, debt_id_instance))

        # Committing the changes to the database
        conn.commit()

        cursor.execute(f"SELECT * FROM debts WHERE id = {committed_debt_id}")
        columns = cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
        debts_df = pd.DataFrame(result)
        debts_df['total_amount'] = debts_df['total_amount'].astype(int)
        debts_df['outstanding'] = debts_df['outstanding'].astype(int)

    # Query the updated row from the expenses table
    cursor.execute(f"SELECT * FROM expenses WHERE id = {expense_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    df['value'] = df['value'].astype(int)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(f"Expense with id {expense_id} updated successfully.", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    if not debts_df.empty:
        print()
        print(colored('IMPACTED DEBTS', 'cyan'))
        print(colored(f"Debt with id {committed_debt_id} updated successfully.", 'cyan'))
        print(colored(tabulate(debts_df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

def fn_delete_expenses_by_ids(called_function_arguments_dict):
    # Extract the id string from the argument dictionary
    ids_str = called_function_arguments_dict.get('ids', '')

    # If ids are not provided, just return
    if not ids_str:
        print("No ids provided to delete.")
        return

    # Split the id string by underscore (_) to get a list of ids
    id_strs = ids_str.split('_')

    # Convert each id string into an integer
    ids = [int(id_str) for id_str in id_strs]

    cursor = conn.cursor()


    print(colored(f"Expenses with ids {ids_str} deleted successfully.", 'cyan'))

    for id_str in id_strs:
        expense_id = int(id_str)
        # print('242', expense_id)

        cursor.execute(f"SELECT debt_id FROM expenses WHERE id = {expense_id}")
        committed_debt_id = cursor.fetchone()[0]
        # print('246', committed_debt_id)

        sql = "DELETE FROM expenses WHERE id = %s"
        # Execute the DELETE command
        cursor.execute(sql, (expense_id,))
        conn.commit()

        if committed_debt_id != 0:

            cursor.execute("SELECT id FROM debts")
            debt_ids = [row[0] for row in cursor.fetchall()]

            for debt_id_instance in debt_ids:
                # Fetch the most recent log of the corresponding debt_id
                cursor.execute("SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id_instance,))
                most_recent_log_date = cursor.fetchone()[0]

                # If most_recent_log_date is None, continue to next iteration
                if most_recent_log_date is None:
                    continue

                # Fetch the total_amount and outstanding on most_recent_log_date
                cursor.execute("""
                    SELECT total_amount, outstanding
                    FROM debt_status_logs
                    WHERE debt_id = %s AND status_date = %s
                """, (debt_id_instance, most_recent_log_date))
                initial_total_amount, initial_outstanding = cursor.fetchone()

                # Fetch the sum of relevant expenses for the current debt_id
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN is_debt_repayment = true THEN -value ELSE value END),
                        COUNT(*)
                    FROM expenses 
                    WHERE debt_id = %s AND expense_date > %s
                """, (debt_id_instance, most_recent_log_date))

                total_value, count = cursor.fetchone()

                # If there are no relevant expenses, continue to next iteration
                if count == 0:
                    continue

                if int(debt_id_instance) == int(DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD):
                    new_total_amount = initial_total_amount + total_value
                    new_outstanding = initial_outstanding + total_value
                    cursor.execute("""
                                UPDATE debts 
                                SET total_amount = %s,
                                    outstanding = %s
                                WHERE id = %s
                            """, (new_total_amount, new_outstanding, debt_id_instance))
                else:
                    new_total_amount = initial_total_amount
                    new_outstanding = initial_outstanding + total_value
                    cursor.execute("""
                                UPDATE debts 
                                SET total_amount = %s,
                                    outstanding = %s
                                WHERE id = %s
                            """, (new_total_amount, new_outstanding, debt_id_instance))

            # Committing the changes to the database
            conn.commit()

            cursor.execute(f"SELECT * FROM debts WHERE id = {committed_debt_id}")
            columns = cursor.description
            result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
            pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
            debts_df = pd.DataFrame(result)
            debts_df['total_amount'] = debts_df['total_amount'].astype(int)
            debts_df['outstanding'] = debts_df['outstanding'].astype(int)

            print()
            print(colored('IMPACTED DEBTS', 'cyan'))
            print(colored(f"Debt with id {committed_debt_id} updated successfully on account of deletion of expense id {expense_id}.", 'cyan'))
            print(colored(tabulate(debts_df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

    # Close the cursor and connection
    cursor.close()
    conn.close()

def fn_display_expenses_line_chart(called_function_arguments_dict):

    cursor = conn.cursor(dictionary=True)


    now = datetime.datetime.now()
    start_of_month = datetime.datetime(now.year, now.month, 1)

    # Calculate the number of days since the start of the month
    days_since_start_of_month = (now - start_of_month).days

    # Extract the days_ago_start and days_ago_end from the argument dict, with default values

    if called_function_arguments_dict.get('days_ago_start') is None:
        days_ago_start = days_since_start_of_month
    else:
        days_ago_start = int(called_function_arguments_dict.get('days_ago_start', days_since_start_of_month))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))

    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')


    is_cumulative = called_function_arguments_dict.get('is_cumulative', "false")



    include_debt_repayment_str = called_function_arguments_dict.get('include_debt_repayment')
    if include_debt_repayment_str == "true":
        # Exclude debt repayment
        heading = f"EXPENSES (INCLUDING DEBT REPAYMENTS) FROM {start_date} TO {end_date}"
        query = "SELECT DATE(expense_date) as date, SUM(value) as total_value FROM expenses WHERE DATE(expense_date) >= %s AND DATE(expense_date) <= %s GROUP BY DATE(expense_date) ORDER BY DATE(expense_date)"
    else:
        # Include all expenses
        heading = f"EXPENSES (EXCLUDING DEBT REPAYMENTS) FROM {start_date} TO {end_date}"
        query = "SELECT DATE(expense_date) as date, SUM(value) as total_value FROM expenses WHERE DATE(expense_date) >= %s AND DATE(expense_date) <= %s AND is_debt_repayment = FALSE GROUP BY DATE(expense_date) ORDER BY DATE(expense_date)"


    # cursor.execute(query)
    cursor.execute(query, (start_date, end_date))
     

    expenses = cursor.fetchall()

    if not expenses:
        print("No expenses found in the specified date range.")
        return

    try:
        values = [float(expense['total_value']) for expense in expenses]

    except ValueError as e:
        print(f"Error converting total_value to float: {e}")
        return

    final_heading = heading
    if is_cumulative != "false":
        values = [sum(values[:i + 1]) for i in range(len(values))]
        final_heading = "CUMULATIVE " + heading

    print(colored(final_heading, 'red'))
    print()
    plt.clc()  # clear previous plot
    plt.plot(values, color="red")
    plt.plotsize(70, 20)
    plt.show()

    cursor.close()
    conn.close()


def fn_log_debts(called_function_arguments_dict):

    cursor = conn.cursor()

    # Set default values
    default_currency = 'INR'
    # default_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # If "currency" and "expense_date" are not in called_function_arguments_dict, set them to the defaults
    currency = called_function_arguments_dict.get('currency', default_currency)
    source = called_function_arguments_dict.get('source')
    total_amount = float(called_function_arguments_dict.get('total_amount'))
    outstanding = float(called_function_arguments_dict.get('outstanding', total_amount))
    interest_rate = float(called_function_arguments_dict.get('interest_rate', 0))

    sql = "INSERT INTO debts (source, total_amount, outstanding, interest_rate, currency) VALUES (%s, %s, %s, %s, %s)"
    values = (source, total_amount, outstanding, interest_rate, currency)
    # Execute the command
    cursor.execute(sql, values)
    last_id = cursor.lastrowid


    # After inserting into the debts table and getting the last_id, insert into the debt_status_logs table
    sql = "INSERT INTO debt_status_logs (debt_id, total_amount, outstanding, status_date) VALUES (%s, %s, %s, NOW())"
    values = (last_id, total_amount, outstanding)
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Get the ID of the last inserted row


    # Query the last inserted row
    cursor.execute(f"SELECT * FROM debts WHERE id = {last_id}")

    # Fetch all columns of the last inserted row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    df['total_amount'] = df['total_amount'].astype(int)
    df['outstanding'] = df['outstanding'].astype(int)



    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_insert_debt_status_log(called_function_arguments_dict):
    # Extract the debt_id from the argument dictionary
    debt_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    total_amount = called_function_arguments_dict.get('total_amount', None)
    outstanding = called_function_arguments_dict.get('outstanding', None)


    # Fetch the most recent entry for this debt_id if total_amount or outstanding are None
    if total_amount is None or outstanding is None:
        cursor.execute("SELECT total_amount, outstanding FROM debt_status_logs WHERE debt_id = %s ORDER BY status_date DESC LIMIT 1", (debt_id,))
        previous_entry = cursor.fetchone()
        if previous_entry:
            if total_amount is None:
                total_amount = previous_entry[0]
            if outstanding is None:
                outstanding = previous_entry[1]
        else:
            print("total_amount and outstanding are required to insert a debt status log.")
            return

    # Get current date in YYYY-MM-DD format using Python
    current_date = datetime.datetime.now().date() # Changed from .strftime('%Y-%m-%d')

    sql_log = "INSERT INTO debt_status_logs (debt_id, total_amount, outstanding, status_date) VALUES (%s, %s, %s, %s)"
    values_log = (debt_id, total_amount, outstanding, current_date)
    cursor.execute(sql_log, values_log)

    # Fetch status_date of the last inserted row
    cursor.execute(f"SELECT status_date FROM debt_status_logs WHERE id = LAST_INSERT_ID()")
    status_date_inserted = cursor.fetchone()[0]

    # Query the most recent status_date from debt_status_logs for the given debt_id
    cursor.execute(f"SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id,))
    max_status_date = cursor.fetchone()[0]

    # Only proceed with the update if the inserted status log is the most recent one
    if status_date_inserted == max_status_date:
        # Prepare the update query
        sql = f"UPDATE debts SET total_amount = %s, outstanding = %s WHERE id = %s"

        # Add the id to the end of the values list for the WHERE clause in the SQL query
        values = (total_amount, outstanding, debt_id)

        # Execute the UPDATE command
        cursor.execute(sql, values)

        # Commit the transaction
        conn.commit()

        print(colored(f"Debt status log for debt id {debt_id} inserted successfully. Debts table updated.", 'cyan'))
        # Fetch the last inserted row
        cursor.execute(f"SELECT * FROM debt_status_logs WHERE id = LAST_INSERT_ID()")
        
        # Fetch all columns of the last inserted row
        columns = cursor.description
        result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        
        # Convert the result to DataFrame
        df = pd.DataFrame(result)
        if 'total_amount' in df.columns:
            df['total_amount'] = df['total_amount'].fillna(0).astype(int)
        if 'outstanding' in df.columns:
            df['outstanding'] = df['outstanding'].fillna(0).astype(int)
        print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
    else:
        print(colored(f"The inserted status log is not the most recent one for debt with id {debt_id}. The 'debts' table was not updated.", 'red'))

    # Close the cursor and connection
    cursor.close()
    conn.close()


def fn_recalculate_debts():
    # Getting a cursor from the connection object
    cursor = conn.cursor()

    # Selecting all the debt_ids from debts table
    cursor.execute("SELECT id FROM debts")
    debt_ids = [row[0] for row in cursor.fetchall()]

    # Iterating through each debt_id
    for debt_id_instance in debt_ids:
        # Fetch the most recent log of the corresponding debt_id
        cursor.execute("SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id_instance,))
        most_recent_log_date = cursor.fetchone()[0]

        # If most_recent_log_date is None, continue to next iteration
        if most_recent_log_date is None:
            continue

        # Fetch the total_amount and outstanding on most_recent_log_date
        cursor.execute("""
            SELECT total_amount, outstanding
            FROM debt_status_logs
            WHERE debt_id = %s AND status_date = %s
        """, (debt_id_instance, most_recent_log_date))
        initial_total_amount, initial_outstanding = cursor.fetchone()

        # Fetch the sum of relevant expenses for the current debt_id
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN is_debt_repayment = true THEN -value ELSE value END),
                COUNT(*)
            FROM expenses 
            WHERE debt_id = %s AND expense_date > %s
        """, (debt_id_instance, most_recent_log_date))

        total_value, count = cursor.fetchone()

        # If there are no relevant expenses, continue to next iteration
        if count == 0:
            continue

        # Update total_amount and outstanding in the debts table
        if int(debt_id_instance) == int(DEFAULT_DEBT_ID_FOR_PRIMARY_CREDIT_CARD):
            new_total_amount = initial_total_amount + total_value
            new_outstanding = initial_outstanding + total_value
            cursor.execute("""
                        UPDATE debts 
                        SET total_amount = %s,
                            outstanding = %s
                        WHERE id = %s
                    """, (new_total_amount, new_outstanding, debt_id_instance))
        else:
            new_total_amount = initial_total_amount
            new_outstanding = initial_outstanding + total_value
            cursor.execute("""
                        UPDATE debts 
                        SET total_amount = %s,
                            outstanding = %s
                        WHERE id = %s
                    """, (new_total_amount, new_outstanding, debt_id_instance))

    # Committing the changes to the database
    conn.commit()

    # Query to get all expenses sorted by expense_date in descending order
    cursor.execute("SELECT * FROM debts ORDER BY interest_rate DESC")

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].fillna(0).astype(int)
    if 'outstanding' in df.columns:
        df['outstanding'] = df['outstanding'].fillna(0).astype(int)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))



def fn_list_debts():

    cursor = conn.cursor()
    # Query to get all expenses sorted by expense_date in descending order
    cursor.execute("SELECT * FROM debts ORDER BY interest_rate DESC")

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].fillna(0).astype(int)
    if 'outstanding' in df.columns:
        df['outstanding'] = df['outstanding'].fillna(0).astype(int)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_list_debt_status_logs(called_function_arguments_dict):

    # Check if the id exists in the dictionary, if not set it to None
    debt_id = called_function_arguments_dict.pop('id', None)

    cursor = conn.cursor()

    if debt_id:
        # Query to get all status logs for the given debt_id sorted by status_date in descending order
        cursor.execute(f"SELECT * FROM debt_status_logs WHERE debt_id = %s ORDER BY status_date DESC", (debt_id,))
    else:
        # Query to get all status logs sorted by status_date in descending order
        cursor.execute("SELECT * FROM debt_status_logs ORDER BY status_date DESC")

    # Fetch all columns
    columns = cursor.description

    # Fetch all rows
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)
    
    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].fillna(0).astype(int)
    if 'outstanding' in df.columns:
        df['outstanding'] = df['outstanding'].fillna(0).astype(int)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Print the data
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))


def fn_update_debt_by_id(called_function_arguments_dict):

    # Extract the id from the argument dictionary
    debt_id = called_function_arguments_dict.pop('id')

    cursor = conn.cursor()

    # First fetch the current state of the debt
    cursor.execute(f"SELECT total_amount, outstanding FROM debts WHERE id = {debt_id}")
    current_debt_state = cursor.fetchone()

    # If 'total_amount' or 'outstanding' are being updated, insert a row into the debt_status_logs table
    if 'total_amount' in called_function_arguments_dict or 'outstanding' in called_function_arguments_dict:
        # If the update operation doesn't include either 'total_amount' or 'outstanding', then use the original value
        total_amount = called_function_arguments_dict.get('total_amount', current_debt_state[0])
        outstanding = called_function_arguments_dict.get('outstanding', current_debt_state[1])

        sql_log = "INSERT INTO debt_status_logs (debt_id, total_amount, outstanding, status_date) VALUES (%s, %s, %s, NOW())"
        values_log = (debt_id, total_amount, outstanding)
        cursor.execute(sql_log, values_log)

    # Prepare the update query
    update_statements = ', '.join(f'{key} = %s' for key in called_function_arguments_dict.keys())
    sql = f"UPDATE debts SET {update_statements} WHERE id = %s"

    # Add the id to the end of the values list for the WHERE clause in the SQL query
    values = tuple(called_function_arguments_dict.values()) + (debt_id,)

    # Execute the UPDATE command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    # Query the updated row
    cursor.execute(f"SELECT * FROM debts WHERE id = {debt_id}")

    # Fetch all columns of the updated row
    columns = cursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

    # Convert the result to DataFrame
    pd.options.display.float_format = lambda x: '{:.2f}'.format(x) if abs(x) < 1000000 else '{:.0f}'.format(x)
    df = pd.DataFrame(result)

    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].fillna(0).astype(int)
    if 'outstanding' in df.columns:
        df['outstanding'] = df['outstanding'].fillna(0).astype(int)


    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(f"Debt with id {debt_id} updated successfully.", 'cyan'))
    print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))

def fn_update_debt_status_log_by_id(called_function_arguments_dict):
    # Extract the id from the argument dictionary
    log_id = called_function_arguments_dict.pop('log_id')

    cursor = conn.cursor()

    # Fetch the debt_id of the current log entry
    cursor.execute(f"SELECT debt_id FROM debt_status_logs WHERE id = %s", (log_id,))
    debt_id = cursor.fetchone()[0]

    # Fetch the most recent status_date from debt_status_logs for the given debt_id
    cursor.execute(f"SELECT MAX(status_date) FROM debt_status_logs WHERE debt_id = %s", (debt_id,))
    max_status_date = cursor.fetchone()[0]

    # Fetch status_date of the current log entry
    cursor.execute(f"SELECT status_date FROM debt_status_logs WHERE id = %s", (log_id,))
    status_date_current = cursor.fetchone()[0]

    # Prepare the update query for debt_status_logs
    update_statements = ', '.join(f'{key} = %s' for key in called_function_arguments_dict.keys())
    sql = f"UPDATE debt_status_logs SET {update_statements} WHERE id = %s"

    # Add the log_id to the end of the values list for the WHERE clause in the SQL query
    values = tuple(called_function_arguments_dict.values()) + (log_id,)

    # Execute the UPDATE command
    cursor.execute(sql, values)

    # Commit the transaction
    conn.commit()

    print(colored(f"Debt status log with id {log_id} updated successfully.", 'cyan'))

    # Only update the debts table if the current log entry is the most recent one
    if status_date_current == max_status_date:
        # Fetch the most recent total_amount and outstanding for this log_id
        cursor.execute("SELECT total_amount, outstanding FROM debt_status_logs WHERE id = %s", (log_id,))
        recent_entry = cursor.fetchone()

        # Update the debts table
        if recent_entry:
            sql_debt = f"UPDATE debts SET total_amount = %s, outstanding = %s WHERE id = %s"
            values_debt = (recent_entry[0], recent_entry[1], debt_id)
            cursor.execute(sql_debt, values_debt)
            conn.commit()
            print(colored(f"Debt with id {debt_id} updated successfully.", 'cyan'))
        else:
            print(colored(f"Could not fetch the most recent entry for log_id {log_id}.", 'red'))
    else:
        print(colored(f"The status log with id {log_id} is not the most recent one for debt with id {debt_id}. The 'debts' table was not updated.", 'red'))

    # Close the cursor and connection
    cursor.close()
    conn.close()

def fn_delete_debts_by_ids(called_function_arguments_dict):
    # Extract the id string from the argument dictionary
    ids_str = called_function_arguments_dict.get('ids', '')

    # If ids are not provided, just return
    if not ids_str:
        print("No ids provided to delete.")
        return

    # Split the id string by underscore (_) to get a list of ids
    id_strs = ids_str.split('_')

    # Convert each id string into an integer
    ids = [int(id_str) for id_str in id_strs]

    cursor = conn.cursor()

    # Prepare the delete query. The format function is used to insert the ids into the SQL query
    sql = f"DELETE FROM debts WHERE id IN ({', '.join(['%s'] * len(ids))})"

    # Execute the DELETE command
    cursor.execute(sql, tuple(ids))

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(f"Debts with ids {ids_str} deleted successfully.", 'cyan'))


def fn_delete_debt_status_logs_by_ids(called_function_arguments_dict):
    # Extract the id string from the argument dictionary
    ids_str = called_function_arguments_dict.get('ids', '')

    # If ids are not provided, just return
    if not ids_str:
        print("No ids provided to delete.")
        return

    # Split the id string by underscore (_) to get a list of ids
    id_strs = ids_str.split('_')

    # Convert each id string into an integer
    ids = [int(id_str) for id_str in id_strs]

    cursor = conn.cursor()

    # Prepare the delete query. The format function is used to insert the ids into the SQL query
    sql = f"DELETE FROM debt_status_logs WHERE id IN ({', '.join(['%s'] * len(ids))})"

    print(f'Executing query: {sql} with parameters: {tuple(ids)}')  # Debug line

    # First, for each id, fetch the corresponding debt_id, so that we can update the 'debts' table later
    cursor.execute(f"SELECT debt_id FROM debt_status_logs WHERE id IN ({', '.join(['%s'] * len(ids))})", tuple(ids))
    debt_ids = [row[0] for row in cursor.fetchall()]

    # Execute the DELETE command
    cursor.execute(sql, tuple(ids))

    # Commit the transaction
    conn.commit()

    # Now for each debt_id, find the most recent debt_status_log and update the 'debts' table
    for debt_id in set(debt_ids):  # Using set() to remove duplicates
        # Query the most recent status_log for this debt_id
        cursor.execute(f"SELECT total_amount, outstanding FROM debt_status_logs WHERE debt_id = %s ORDER BY status_date DESC LIMIT 1", (debt_id,))
        row = cursor.fetchone()
        
        if row is not None:
            # If a row was found, update the 'debts' table with these values
            total_amount, outstanding = row
            cursor.execute(f"UPDATE debts SET total_amount = %s, outstanding = %s WHERE id = %s", (total_amount, outstanding, debt_id))
            conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print(colored(f"Debt status logs with ids {ids_str} deleted successfully.", 'cyan'))

def fn_display_debt_status_logs_line_chart(called_function_arguments_dict):


    cursor = conn.cursor(dictionary=True)

    debt_id = called_function_arguments_dict.pop('debt_id')
    # Extract the days_ago_start and days_ago_end from the argument dict, with default values
    days_ago_start = int(called_function_arguments_dict.get('days_ago_start', 30))
    days_ago_end = int(called_function_arguments_dict.get('days_ago_end', 0))


    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_start)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago_end)).strftime('%Y-%m-%d')

    query = f"SELECT DATE(status_date) as date, SUM(outstanding) as total_value FROM debt_status_logs WHERE debt_id = {debt_id} AND DATE(status_date) >= '{start_date}' AND DATE(status_date) <= '{end_date}' GROUP BY DATE(status_date) ORDER BY DATE(status_date)"
    # print(query)
    cursor.execute(query) 
     
     
    debt_status_logs = cursor.fetchall()
    # print(debt_status_logs)

    if not debt_status_logs:
        print("No debt status logs found in the specified date range.")
        return

    try:
        values = [float(log['total_value']) for log in debt_status_logs]


    except ValueError as e:
        print(f"Error converting total_value to float: {e}")
        return

    heading = f"DEBT ID {debt_id} (OUTSTANDING) FROM {start_date} TO {end_date}"
    # print(heading)


    plt.clc()  # clear previous plot
    plt.plot(values, color="red")
    plt.plotsize(70, 20)
    plt.title(heading)
    plt.show()

    cursor.close()
    conn.close()

