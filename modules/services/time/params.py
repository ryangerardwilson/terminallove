import calendar
import datetime
import pytz
import os
from dotenv import load_dotenv

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


schedule_event = {
  "name": "schedule_event",
  "description": "Log an event the user needs to attend to",
  "parameters": {
    "type": "object",
    "properties": {
      "event": {
        "type": "string",
        "description": "The name of the event"
      },
      "date": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": "The date of the event in YYYY-MM-DD format."
      },
      "time": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": "The time of the event in HH:MM:SS format."
        },
      "today": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "enum": [today]
      }
    },
    "required": ["event"]
  }
}

list_events = {
    "name": "list_events",
    "description": "Lists the user's calendered and docketed events",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing events from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

update_event_by_id = {
    "name": "update_event_by_id",
    "description": "Update an event by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Event id"
            },
            "event": {
                "type": "string",
                "description": "The name of the event"
            },
            "date": {
              "type": "string",  # Python doesn't have a built-in timestamp data type
              "description": "The date of the event in YYYY-MM-DD format."
            },
            "time": {
              "type": "string",  # Python doesn't have a built-in timestamp data type
              "description": "The time of the event in HH:MM:SS format."
              },
        },
        "required": ["id"]
    }
}

delete_events_by_ids = {
    "name": "delete_events_by_ids",
    "description": "Delete events by their ids",
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

tell_me_the_date = {
  "name": "tell_me_the_date",
  "description": "Tell me the date",
  "parameters": {
    "type": "object",
    "properties": {
      "timestamp": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": f"Today's date i.e. {today} printed in YYYY-MM-DD HH:MM:SS format"
      },
      "day": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": f"Today's day i.e. {day}"
      },
    },
    "required": ["timestamp", "day"]
  }
}

tell_me_the_days_left_in_the_current_month = {
  "name": "tell_me_the_days_left_in_the_current_month",
  "description": "Tell me the days left in in the current month",
  "parameters": {
    "type": "object",
    "properties": {
      "days": {
        "type": "string",  # Python doesn't have a built-in timestamp data type
        "description": f"{days_left_in_current_month} days left in the current month"
      },
    },
    "required": ["days"]
  }
}

tell_me_the_days_left_in_the_current_year = {
  "name": "tell_me_the_days_left_in_the_current_year",
  "description": "Tell me the days left in in the current year",
  "parameters": {
    "type": "object",
    "properties": {
      "days": {
        "type": "integer",  # Python doesn't have a built-in timestamp data type
        "description": f"{days_left_in_current_year} days left in the current year"
      },
    },
    "required": ["days"]
  }
}
