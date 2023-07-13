import csv
import os
from termcolor import colored
import os
import json
import aiohttp
import asyncio
import argparse
from modules.services.nonAiHelpers.utilities.functions import *

# Interaction history file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
history_file = os.path.join(parent_dir, "history.csv")

# Function to load history from file
def load_history() -> list:
    if not os.path.exists(history_file):
        return [{"role": "system", "content": "You are a helpful assistant."}]
    else:
        history = []
        with open(history_file, 'r') as f:
            reader = csv.DictReader(f)
            history = [row for row in reader]
        return history

# Function to save history to file
def save_history(history: list) -> None:
    with open(history_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["role", "content"])
        writer.writeheader()
        for message in history:
            writer.writerow(message)

# Function to clear history
def clear_history() -> None:
    if os.path.exists(history_file):
        os.remove(history_file)

def process_hard_coded_flags(reset, p_action, p, l, m, id, service, username, password, comments, vm, db, vm_action, db_action, command, description):

    function_invoked = False


    if reset:
        clear_history()
        print("Interaction history cleared.")
        function_invoked = True

    # if d:
    #     fn_display_rgw_database_schema()
    #     function_invoked = True

    if p_action != None:
        # Check if action is 'create'
        if p_action == 'create':
            # Check if all required arguments are present
            if service and username and password:
                fn_create_password(service, username, password, comments)
            else:
                print(colored("\nExample of correct syntax for create: --p:create --service 'gmail' --username '100smoochiekisses@gmail.com' --password 'ainiwmn' --comments 'Oooolalalala'", 'cyan'))
            function_invoked = True
        # Check if action is 'update'
        elif p_action == 'update':
            # Check if all required arguments are present
            if id and (service != '' or username != '' or password != '' or comments != None):
                fn_update_password(id, service, username, password, comments)
            else:
                print(colored("Examples of correct syntax for update:", 'cyan'))
                print(colored("--p:update --id '3' --service 'gmail'", 'cyan'))
                print(colored("--p:update --id '3' --username '100smoochiekisses@gmail.com'", 'cyan'))
                print(colored("--p:update --id '3' --password 'ainiwmn'", 'cyan'))
                print(colored("--p:update --id '3' --comments 'ooolalala'", 'cyan'))
                print(colored("--p:update --id '3' --service 'gmail' --username '100smoochiekisses@gmail.com' --password 'ainiwmn' --comments 'Ooolalal'", 'cyan'))
            function_invoked = True
        # Check if action is 'delete'
        elif p_action == 'delete':
            # Check if all required arguments are present
            if id:
                fn_delete_password(id)
            else:
                print("\nExample of correct syntax for delete: --p:delete --id '3'")
            function_invoked = True
        # Check if action is 'read'
        elif p_action == 'read' or p:
            fn_display_passwords()
            function_invoked = True

    if l:
        fn_display_functionalities()
        function_invoked = True




    # Check if action is 'create'
    if vm_action == 'create':
        # Check if all required arguments are present
        # print(command, description)
        if command and description:
            fn_create_vm_record(description, command, password)
        else:
            print(colored("\nExample of correct syntax for create: --vm:create --description 'Digital Ocean Data Analytics Server' --command 'ssh@123.123.123.123'", 'cyan'))
        function_invoked = True
    # Check if action is 'update'
    elif vm_action == 'update':
        # Check if all required arguments are present
        if id and (command != '' or description != '' or password != None):
            fn_update_vm_record(id, description, command, password)
        else:
            print(colored("Examples of correct syntax for update:", 'cyan'))
            print(colored("--vm:update --id '3' --description 'Fancy Frontend Server'", 'cyan'))
            print(colored("--vm:update --id '3' --command 'ssh@456.456.456.456'", 'cyan'))
            print(colored("--vm:update --id '3' --description 'Fancy Frontend Server' --command 'ssh@456.456.456.456'", 'cyan'))
        function_invoked = True
    # Check if action is 'delete'
    elif vm_action == 'delete':
        # Check if all required arguments are present
        if id:
            fn_delete_vm_record(id)
        else:
            print("\nExample of correct syntax for delete: --ssh:delete --id '3'")
        function_invoked = True
    # Check if action is 'read'
    elif vm and id != 0 and id != None:
        fn_ssh_into_vm(id)
        function_invoked = True
    elif vm_action == 'read' or vm:
        fn_display_vm_records()
        function_invoked = True





    # Check if action is 'create'
    if db_action == 'create':
        # Check if all required arguments are present
        # print(command, description)
        if command and description:
            fn_create_db_record(description, command, password)
        else:
            print(colored("\nExample of correct syntax for create: --db:create --description 'Dream database' --command 'mysql -h \"34.131.86.7\" -u \"root\" -p\"isadhishaid8\" \"rgw\"'", 'cyan'))
        function_invoked = True
    # Check if action is 'update'
    elif db_action == 'update':
        # Check if all required arguments are present
        if id and (command != '' or description != '' or password != None):
            fn_update_db_record(id, description, command, password)
        else:
            print(colored("Examples of correct syntax for update:", 'cyan'))
            print(colored("--db:update --id '3' --description 'Dream Prod Database'", 'cyan'))
            print(colored("--db:update --id '3' --command 'mysql -h \"34.131.86.7\" -u \"root\" -p\"isadhishaid8\" \"rgw\"'", 'cyan'))
            print(colored("--db:update --id '3' --description 'Dream Prod Database' --command 'mysql -h \"34.131.86.7\" -u \"root\" -p\"isadhishaid8\" \"rgw\"'", 'cyan'))
        function_invoked = True
    # Check if action is 'delete'
    elif db_action == 'delete':
        # Check if all required arguments are present
        if id:
            fn_delete_db_record(id)
        else:
            print("\nExample of correct syntax for delete: --db:delete --id '3'")
        function_invoked = True
    elif db_action == 'schema':
        if id:
            fn_display_db_schema(id)
        else:
            print("\nExample of correct syntax for printing schema: --db:schema --id '3'")
        function_invoked = True
    # Check if action is 'read'
    elif db and id != 0 and id != None:
        fn_mysql_connect_to_db(id)
        function_invoked = True
    elif db_action == 'read' or db:
        fn_display_db_records()
        function_invoked = True

    return function_invoked

async def spinning_loader():
    """ASCII spinning loader animation"""
    animation_chars = ['|', '/', '-', '\\']
    idx = 0
    try:
        while True:
            sys.stdout.write(colored('\r' + animation_chars[idx % 4], 'cyan'))
            idx += 1
            sys.stdout.flush()
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        sys.stdout.write('\r \r')
        sys.stdout.flush()


async def make_ordinary_call_to_open_ai(url, headers, data, interaction_history):
    response = ''
    last_response = ''

    function_call_invoked = False
    called_function_name = ''
    called_function_arguments = ''
    most_recent_arguments = ''

    error_count = 0
    # Send the request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            async for line in resp.content:
                # Ignore newline characters
                if line == b'\n':
                    continue

                if b': ' in line:
                    key, value = line.split(b': ', 1)

                    # Only process 'data' lines
                    if key == b'data':
                        try:
                            json_line = json.loads(value)


                            # Append delta content to the response
                            response += json_line['choices'][0]['delta'].get('content', '')

                            # If there is new content, print it
                            if response != last_response:
                                new_content = response[len(last_response):]
                                if 'function_call' not in json_line.get('choices', [{}])[0].get('delta', {}):
                                    sys.stdout.write(colored(new_content, 'cyan'))
                                sys.stdout.flush()
                                last_response = response

                            # If the message is finished, save the response to the interaction history and persist it to the file
                            if 'finish_reason' in json_line['choices'][0] and json_line['choices'][0][
                                'finish_reason'] == 'stop':
                                interaction_history.append({"role": "assistant", "content": response.strip()})
                                save_history(interaction_history)
                        except json.JSONDecodeError as e:
                            # Handle non-JSON lines
                            # if 'function_call' not in json_line.get('choices', [{}])[0].get('delta', {}):
                            if value != b'[DONE]\n':
                                print('Non-JSON line:', value)

                else:
                    error_count = error_count + 1
                    if error_count == 1:
                        print(colored(f'OpenAI returned an unexpected line format: {line}', 'red'))
                        print(colored(f'Resetting the bot may help', 'red'))

    return None
async def make_functions_call_to_open_ai(url, headers, data):
    response = ''
    last_response = ''
    called_function_name = ''
    called_function_arguments = ''
    most_recent_arguments = ''
    error_count = 0

    # Send the request
    async with aiohttp.ClientSession() as session:
        animation = asyncio.create_task(spinning_loader())
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            async for line in resp.content:
                # Ignore newline characters
                if line == b'\n':
                    continue

                if b': ' in line:
                    key, value = line.split(b': ', 1)

                    # Only process 'data' lines
                    if key == b'data':
                        try:
                            json_line = json.loads(value)

                            if 'function_call' in json_line.get('choices', [{}])[0].get('delta', {}):
                                if 'name' in json_line['choices'][0]['delta']['function_call']:
                                    called_function_name = json_line['choices'][0]['delta']['function_call']['name']

                                if 'arguments' in json_line['choices'][0]['delta']['function_call']:
                                    called_function_arguments_str = json.dumps(json_line['choices'][0]['delta']['function_call']['arguments'])
                                    called_function_arguments += called_function_arguments_str

                                    if 'finish_reason' in json_line['choices'][0] and json_line['choices'][0][
                                        'finish_reason'] != 'function_call':
                                        most_recent_arguments = called_function_arguments

                        except json.JSONDecodeError as e:
                            # Handle non-JSON lines
                            if value != b'[DONE]\n':
                                print('Non-JSON line:', value)
                        except Exception as e:
                            print("Unexpected error:", e)

        animation.cancel()

    if called_function_name and most_recent_arguments:
        s0 = most_recent_arguments.replace('"""{\\n', "").replace('"\\n""}"', "").replace('\\n""', "")
        s1 = ''.join([char for char in s0 if char not in ["\\n"]])
        s2 = ''.join([char for char in s1 if char not in ["'"]])
        s3 = ''.join([char for char in s2 if char not in ['"']])
        s4 = ''.join([char for char in s3 if char not in ["\\"]])

        # Remove the leading and trailing curly braces if they exist
        s4 = s4.strip()
        if s4.startswith('{'):
            s4 = s4[1:]
        if s4.endswith('}'):
            s4 = s4[:-1]

        # Split the string to separate keys and values
        items = s4.split(",")

        # Create a dictionary
        arguments_dict = {}
        for item in items:
            key_value = item.split(":")
            key = key_value[0].strip()
            value = ":".join(key_value[1:]).strip()
            arguments_dict[key] = value

        return {"function_name": called_function_name, "arguments": arguments_dict}

    return None


invoke_finance_module = {
    "name": "invoke_finance_module",
    "description": "Invokes a library of functions that manage the user's finances",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Module invoked"]
            },
        },
        "required": []
    }
}

invoke_goals_module = {
    "name": "invoke_goals_module",
    "description": "Invokes a library of functions that manage the user's goals, timesheets, and actions",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Module invoked"]
            },
        },
        "required": []
    }
}

invoke_runs_module = {
    "name": "invoke_runs_module",
    "description": "Invokes a library of functions that manage the user's runs",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Module invoked"]
            },
        },
        "required": []
    }
}

invoke_time_module = {
    "name": "invoke_time_module",
    "description": "Invokes a library of functions that manage the user's time, calender and events",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Module invoked"]
            },
        },
        "required": []
    }
}



