import calendar
import datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')


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




