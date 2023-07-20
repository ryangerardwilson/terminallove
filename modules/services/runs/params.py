import calendar
import datetime
import os
import pytz

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

now = datetime.datetime.now(tz)
weekday_num = now.weekday()
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day = days_of_week[weekday_num]
today = now.strftime('%Y-%m-%d %H:%M:%S')
days_in_current_month = calendar.monthrange(now.year, now.month)[1]
days_left_in_current_month = days_in_current_month - now.day
last_day_of_current_year = datetime.datetime(now.year, 12, 31, tzinfo=tz)
days_left_in_current_year = (last_day_of_current_year - now).days


list_run_logging_params = {
    "name": "list_run_logging_params",
    "description": "If user is confused, list the parameters required to log a run",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing runs from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

add_run_logs = {
  "name": "add_run_logs",
  "description": "Adds/logs the user's run to the runs table",
  "parameters": {
    "type": "object",
    "properties": {
      "pre_run_weight_lbs": {
        "type": "integer",
        "description": "The user's weight in kgs before the run"
      },
      "post_run_weight_lbs": {
        "type": "integer",
        "description": "The user's weight in kgs after the run"
      },
      "fat_burn_zone_minutes": {
        "type": "integer",
        "description": "The time spent by the user in the fat burn zone"
      },
      "cardio_zone_minutes": {
        "type": "integer",
        "description": "The time spent by the user in the cardio zone"
      },
      "peak_zone_minutes": {
        "type": "integer",
        "description": "The time spent by the user in the peak zone"
      },
      "distance_covered_kms": {
        "type": "integer",
        "description": "The distance covered during the run"
      },
     "temperature_in_f": {
        "type": "integer",
        "description": "The average temperature during the run"
      },
      "date": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": "The date of the run in YYYY-MM-DD format."
      },
      "today": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "enum": [today]
      }
    },
    "required": []
  }
}


list_run_logs = {
    "name": "list_run_logs",
    "description": "Lists the user's runs",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing runs from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}


update_run_by_id = {
    "name": "update_run_by_id",
    "description": "Update a run log by its id i.e. the run id",
    "parameters": {
        "type": "object",
        "properties": {
            "run_id": {
                "type": "integer",
                "description": "Run id"
            },
            "goal_id": {
                "type": "integer",
                "description": "The goal id of the run. Default is 2"
            },
            "action_id": {
                "type": "integer",
                "description": "The action id of the run. Default is 2"
            },
            "pre_run_weight_lbs": {
                "type": "integer",
                "description": "The user's weight in kgs before the run"
            },
            "post_run_weight_lbs": {
                "type": "integer",
                "description": "The user's weight in kgs after the run"
            },
            "fat_burn_zone_minutes": {
                "type": "integer",
                "description": "The time spent by the user in the fat burn zone"
            },
            "cardio_zone_minutes": {
                "type": "integer",
                "description": "The time spent by the user in the cardio zone"
            },
            "peak_zone_minutes": {
                "type": "integer",
                "description": "The time spent by the user in the peak zone"
            },
            "distance_covered_kms": {
                "type": "integer",
                "description": "The distance covered during the run"
            },
            "temperature_in_f": {
                "type": "integer",
                "description": "The average temperature during the run in Fahrenheit"
            },
            "date": {
                "type": "string",  # Python doesn't have a built-in timestamp data type
                "description": "The date of the run in YYYY-MM-DD format."
            },
            "today": {
                "type": "string",  # Python doesn't have a built-in timestamp data type
                "enum": [today]
            }
        },
        "required": ["run_id"]
    }
}

delete_runs_by_ids = {
    "name": "delete_runs_by_ids",
    "description": "Delete runs by their ids",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

list_available_running_charts = {
    "name": "list_available_running_charts",
    "description": "Lists the available running charts",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing running charts from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

display_running_weight_line_chart = {
    "name": "display_running_weight_line_chart",
    "description": "Plots an ascii line chart of the user's weight over the given range of days",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. Default is 30."
            },
            "today": {
                "type": "string",
                "enum": [today]
            },
        },
        "required": []
    }
}


display_runs_fat_burn_line_chart = {
    "name": "display_runs_fat_burn_line_chart",
    "description": "Plots an ascii line chart of the user's fat burn / zone 2 running minutes over the given range of days",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. Default is 30."
            },
            "is_cumulative": {
                "type": "boolean",
                "description": "If the user has requested cumulative expenses. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            },
        },
        "required": ["is_cumulative"]
    }
}

display_runs_distance_line_chart = {
    "name": "display_runs_distance_line_chart",
    "description": "Plots an ascii line chart of the user's distance covered while running over the given range of days",
    "parameters": {
        "type": "object",
        "properties": {
            "days_ago_end": {
                "type": "integer",
                "description": "The number of days ago when the range ends. Default is 0."
            },
            "days_ago_start": {
                "type": "integer",
                "description": "The number of days ago when the range starts. Default is 30."
            },
            "is_cumulative": {
                "type": "boolean",
                "description": "If the user has requested cumulative expenses. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            },
        },
        "required": ["is_cumulative"]
    }
}
