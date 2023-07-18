import calendar
import datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')

list_cronjobs = {
  "name": "list_cronjobs",
  "description": "Lists the user's cronjobs",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Listing cronjobs"]
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




