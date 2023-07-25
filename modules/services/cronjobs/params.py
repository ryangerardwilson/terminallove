import calendar
import datetime
import os
import pytz
from dotenv import load_dotenv

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

now = datetime.datetime.now(tz)
today = now.strftime('%Y-%m-%d %H:%M:%S')

list_cronjobs_module_functions = {
    "name": "list_cronjobs_module_functions",
    "description": "Lists functions in the Cronjobs module",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing functions from Cronjobs module"]
            },
        },
        "required": []
    }
}

inspect_cronjob_logs_by_id = {
  "name": "inspect_cronjob_logs_by_id",
  "description": "Inspects cron job logs by id",
  "parameters": {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "description": "The id of the cron job log"
        },
     },
    "required": ["id"]
  }
}

list_cronjobs = {
  "name": "list_cronjobs",
  "description": "Lists the user's cronjobs",
  "parameters": {
    "type": "object",
    "properties": {
        "connection": {
            "type": "string",
            "enum": ["Listing functions from Twitter module"]
        },
    },
    "required": []
  }
}

list_cronjob_logs = {
  "name": "list_cronjob_logs",
  "description": "Lists the user's cronjob logs",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of logs to list out"
       },
     },
    "required": []
  }
}

clear_cronjob_logs = {
  "name": "clear_cronjob_logs",
  "description": "Clears, deletes, truncates the user's cronjob logs",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Truncating cronjob_logs table"]
       },
     },
    "required": []
  }
}

activate_cronjobs = {
  "name": "activate_cronjobs",
  "description": "Activates the user's cron jobs",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Activating cron jobs"]
       },
     },
    "required": []
  }
}

deactivate_cronjobs = {
  "name": "deactivate_cronjobs",
  "description": "De-activates the user's cron jobs",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["De-activating cron jobs"]
       },
     },
    "required": []
  }
}




