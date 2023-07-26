#!/usr/bin/env python3
import os
import asyncio
import argparse

from modules.botHelpers import *

from modules.services.finance.params import *
from modules.services.time.params import *
from modules.services.goals.params import *
from modules.services.runs.params import *
from modules.services.twitter.params import *
from modules.services.notes.params import *
from modules.services.cronjobs.params import *
from modules.services.blogposts.params import *

from modules.services.finance.functions import *
from modules.services.time.functions import *
from modules.services.goals.functions import *
from modules.services.runs.functions import *
from modules.services.twitter.functions import *
from modules.services.notes.functions import *
from modules.services.cronjobs.functions import *
from modules.services.blogposts.functions import *

from modules.services.nonAiHelpers.utilities.functions import *

async def main(
        user_message: str,
        update: bool = False,
        reset: bool = False,
        locate:bool = False,
        mod: str = '',
        p_action = None,
        p: bool = False,
        l: bool = False,
        id: int = 0,
        service: str = '',
        username: str = '',
        password: str = '',
        comments = None,
        vm: bool = False,
        db: bool = False,
        vm_action = None,
        db_action=None,
        command: str = '',
        description: str = ''
    ):

    # Fetch API key from environment variables
    api_key = os.getenv('OPEN_AI_API_KEY')
    gpt_model = os.getenv('GPT_MODEL')
    preliminary_classification_functions = [
        invoke_cronjobs_module,
        invoke_finance_module,
        invoke_goals_module,
        invoke_runs_module,
        invoke_time_module,
        invoke_notes_module,
        invoke_twitter_module,
        invoke_blogposts_module,
    ]

    # Define the URL
    url = "https://api.openai.com/v1/chat/completions"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Load the interaction history
    interaction_history = load_history()

    function_invoked = process_hard_coded_flags(update, reset, locate, p_action, p, l, id, service, username, password, comments, vm, db, vm_action, db_action, command, description)

    if function_invoked:
        return

    # Add the user message to the interaction history
    interaction_history.append({"role": "user", "content": user_message})
    if mod != '':
        interaction_history.append({"role": "system", "content": f"Sound like {mod}"})

    preliminary_classification_data = {
        "model": gpt_model,
        "messages": interaction_history,
        "stream": True,
        "functions": preliminary_classification_functions,
        "function_call": "auto",
    }

    preliminary_classification_function_info = await make_functions_call_to_open_ai(url, headers, preliminary_classification_data)

    if preliminary_classification_function_info == None:

        classification_data = {
            "model": gpt_model,
            "messages": interaction_history,
            "stream": True,
        }

        await make_ordinary_call_to_open_ai(url, headers, classification_data, interaction_history)

    else:
        functions = []
        
        if preliminary_classification_function_info['function_name'] == 'invoke_cronjobs_module':
            functions =[
                list_cronjobs_module_functions,
                inspect_cronjob_logs_by_id,
                list_cronjobs,
                list_cronjob_logs,
                clear_cronjob_logs,
                activate_cronjobs,
                deactivate_cronjobs,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_finance_module':
            functions =[
                list_finance_module_functions,
                list_expense_logging_params,
                log_expenses,
                log_debt_repayment,
                list_expenses,
                update_expense_by_id,
                delete_expenses_by_ids,
                display_expenses_line_chart,

                log_debts,
                insert_debt_status_log,
                recalculate_debts,
                list_debts,
                list_debt_status_logs,
                update_debt_by_id,
                update_debt_status_log_by_id,
                delete_debts_by_ids,
                delete_debt_status_logs_by_ids,
                display_debt_status_logs_line_chart,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_goals_module':
            functions = [
                add_goal,
                list_goals,
                update_goal_by_id,
                delete_goals_by_ids,

                add_reason,
                list_reasons_by_goal_id,
                update_reason_by_id,
                delete_reasons_by_ids,

                add_action,
                list_actions,
                list_actions_by_goal_id,
                update_action_by_id,
                delete_actions_by_ids,

                add_timesheet_logs,
                list_timesheet_logs,
                delete_timesheet_logs,
                display_timesheets_line_chart,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_runs_module':
            functions = [
                list_run_logging_params,
                add_run_logs,
                list_run_logs,
                update_run_by_id,
                delete_runs_by_ids,
                list_available_running_charts,
                display_running_weight_line_chart,
                display_runs_fat_burn_line_chart,
                display_runs_distance_line_chart,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_time_module':
            functions = [
                schedule_event,
                list_events,
                update_event_by_id,
                delete_events_by_ids,
                tell_me_the_date,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_notes_module':
            functions = [
                open_note,
                open_most_recent_note,
                open_most_recently_edited_note,
                save_and_close_notes,
                delete_local_note_cache,
                list_notes,
                delete_notes_by_ids,
                add_or_update_media_to_notes_by_ids,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_twitter_module':
            functions = [
                list_twitter_module_functions,
                list_rate_limits,
                list_tweets,
                list_queued_tweets,
                list_spaced_tweets,
                tweet_out_note,
                schedule_tweet,
                edit_tweet,
                delete_tweets_by_ids,
                delete_tweets_by_note_ids,
                delete_queued_tweets_by_ids,
                delete_queued_tweets_by_note_ids,
                delete_spaced_tweets_by_ids,
                delete_spaced_tweets_by_note_ids,
            ]

        if preliminary_classification_function_info['function_name'] == 'invoke_blogposts_module':
            functions = [
                list_blogposts,
                post_note_to_blog,
                edit_blogpost,
                delete_blogposts_by_ids,
            ]

        classification_data = {
            "model": gpt_model,
            "messages": interaction_history,
            "stream": True,
            "functions": functions,
            "function_call": "auto",
        }

        classification_function_info = await make_functions_call_to_open_ai(url, headers, classification_data)
        
        if classification_function_info:
            print(colored('Function Invoked: ' + classification_function_info["function_name"] + json.dumps(classification_function_info["arguments"]),
                          'yellow'))

            # Mapping functions that require arguments
            functions_with_args = {
                'log_expenses': fn_log_expenses,
                'log_debt_repayment': fn_log_debt_repayment,
                'list_expenses': fn_list_expenses,
                'update_expense_by_id': fn_update_expense_by_id,
                'delete_expenses_by_ids': fn_delete_expenses_by_ids,
                'display_expenses_line_chart': fn_display_expenses_line_chart,
                'log_debts': fn_log_debts,
                'insert_debt_status_log': fn_insert_debt_status_log,
                'list_debt_status_logs': fn_list_debt_status_logs,
                'update_debt_by_id': fn_update_debt_by_id,
                'update_debt_status_log_by_id': fn_update_debt_status_log_by_id,
                'delete_debts_by_ids': fn_delete_debts_by_ids,
                'delete_debt_status_logs_by_ids': fn_delete_debt_status_logs_by_ids,
                'display_debt_status_logs_line_chart': fn_display_debt_status_logs_line_chart,
                'schedule_event': fn_schedule_event,
                'update_event_by_id': fn_update_event_by_id,
                'delete_events_by_ids': fn_delete_events_by_ids,
                'add_goal': fn_add_goal,
                'update_goal_by_id': fn_update_goal_by_id,
                'delete_goals_by_ids': fn_delete_goals_by_ids,
                'add_reason': fn_add_reason,
                'list_reasons_by_goal_id': fn_list_reasons_by_goal_id,
                'update_reason_by_id': fn_update_reason_by_id,
                'delete_reasons_by_ids': fn_delete_reasons_by_ids,
                'add_action': fn_add_action,
                'list_actions_by_goal_id': fn_list_actions_by_goal_id,
                'update_action_by_id': fn_update_action_by_id,
                'delete_actions_by_ids': fn_delete_actions_by_ids,
                'add_timesheet_logs': fn_add_timesheet_logs,
                'list_timesheet_logs': fn_list_timesheet_logs,
                'delete_timesheet_logs': fn_delete_timesheet_logs,
                'display_timesheets_line_chart': fn_display_timesheets_line_chart,
                'add_run_logs': fn_add_run_logs,
                'update_run_by_id': fn_update_run_by_id,
                'delete_runs_by_ids': fn_delete_runs_by_ids,
                'display_running_weight_line_chart': fn_display_running_weight_line_chart,
                'display_runs_fat_burn_line_chart': fn_display_runs_fat_burn_line_chart,
                'display_runs_distance_line_chart': fn_display_runs_distance_line_chart,
                'open_note': fn_open_note,
                'delete_notes_by_ids': fn_delete_notes_by_ids,
                'list_notes': fn_list_notes,
                'tweet_out_note': fn_tweet_out_note,
                'list_tweets': fn_list_tweets,
                'list_queued_tweets': fn_list_queued_tweets,
                'list_spaced_tweets': fn_list_spaced_tweets,
                'schedule_tweet': fn_schedule_tweet,
                'edit_tweet': fn_edit_tweet,
                'delete_tweets_by_ids': fn_delete_tweets_by_ids,
                'delete_tweets_by_note_ids': fn_delete_tweets_by_note_ids,
                'delete_queued_tweets_by_ids': fn_delete_queued_tweets_by_ids,
                'delete_queued_tweets_by_note_ids': fn_delete_queued_tweets_by_note_ids,
                'delete_spaced_tweets_by_ids': fn_delete_spaced_tweets_by_ids,
                'delete_spaced_tweets_by_note_ids': fn_delete_spaced_tweets_by_note_ids,
                'add_or_update_media_to_notes_by_ids': fn_add_or_update_media_to_notes_by_ids,
                'list_cronjob_logs': fn_list_cronjob_logs,
                'inspect_cronjob_logs_by_id': fn_inspect_cronjob_logs_by_id,
                'open_most_recent_note': fn_open_most_recent_note,
                'open_most_recently_edited_note': fn_open_most_recently_edited_note,
            }

            # Mapping functions that do not require arguments
            functions_without_args = {
                'list_finance_module_functions': fn_list_finance_module_functions,
                'list_cronjobs_module_functions': fn_list_cronjobs_module_functions,
                'list_twitter_module_functions': fn_list_twitter_module_functions,
                'list_expense_logging_params': fn_list_expense_logging_params,
                'recalculate_debts': fn_recalculate_debts,
                'list_debts': fn_list_debts,
                'list_events': fn_list_events,
                'list_goals': fn_list_goals,
                'list_actions': fn_list_actions,
                'list_run_logging_params': fn_list_run_logging_params,
                'list_run_logs': fn_list_run_logs,
                'list_available_running_charts': fn_list_available_running_charts,
                'save_and_close_notes': fn_save_and_close_notes,
                'delete_local_note_cache': fn_delete_local_note_cache,
                'list_rate_limits': fn_list_rate_limits,
                'activate_cronjobs': fn_activate_cronjobs,
                'deactivate_cronjobs': fn_deactivate_cronjobs,
                'list_cronjobs': fn_list_cronjobs,
                'clear_cronjob_logs': fn_clear_cronjob_logs,
            }

            # Get function name and arguments
            function_name = classification_function_info['function_name']
            arguments = classification_function_info.get('arguments', None)

            # Call the function with arguments
            if function_name in functions_with_args:
                functions_with_args[function_name](arguments)

            # Call the function without arguments
            elif function_name in functions_without_args:
                functions_without_args[function_name]()

            # Function name not recognized

    print()

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description='Interact with OpenAI GPT-3.')
    parser.add_argument('user_message', type=str, nargs='?', default='', help='User message to send to GPT-3')
    parser.add_argument('--reset', action='store_true', help='Reset the context of the conversation')
    parser.add_argument('--mod', type=str, nargs='?', default='')

    # parser.add_argument('--d', action='store_true', help='List out schema of rgw database')
    parser.add_argument('--l', action='store_true', help='List out all functionalities')

    # Modified argument for password actions
    parser.add_argument('--p', action='store_true', help='Password actions: create, read, update, or delete in --p:action format')
    parser.add_argument('--id', type=int, help='ID of the record to reference')
    parser.add_argument('--service', type=str, help='Service name')
    parser.add_argument('--username', type=str, help='Username')
    parser.add_argument('--password', type=str, help='Password')
    parser.add_argument('--comments', type=str, help='Comments')

    parser.add_argument('--vm', action='store_true', help='VM actions: create, read, update, or delete in --vm:action format')
    parser.add_argument('--db', action='store_true', help='DB actions: create, read, update, delete, or get schema in --db:action format')
    parser.add_argument('--command', type=str, help='SSH command name')
    parser.add_argument('--description', type=str, help='SSH command description')
    
    # Modified argument for password actions
    parser.add_argument('--update', action='store_true', help='Updates the bot from the latest version in the git repository')
    parser.add_argument('--locate', action='store_true', help='Locates the bot directory')

    # Parse known and unknown args
    args, unknown = parser.parse_known_args()

    # Check for the --p:action format
    p_action = None
    vm_action = None
    db_action = None
    for arg in unknown:
        if arg.startswith("--p:"):
            p_action = arg.split(":")[1]

        if arg.startswith("--vm:"):
            vm_action = arg.split(":")[1]

        if arg.startswith("--db:"):
            db_action = arg.split(":")[1]

    if args.p and p_action is None:
        p_action = 'read'

    if args.vm and vm_action is None:
        vm_action = 'read'

    if args.db and db_action is None:
        db_action = 'read'

    # Modified argument for password actions


    # Run the main function
    asyncio.run(
        main(
            args.user_message,
            args.update,
            args.reset,
            args.locate,
            args.mod,
            p_action,
            args.p,
            args.l,
            args.id,
            args.service,
            args.username,
            args.password,
            args.comments,
            args.vm,
            args.db,
            vm_action,
            db_action,
            args.command,
            args.description
        )
    )


