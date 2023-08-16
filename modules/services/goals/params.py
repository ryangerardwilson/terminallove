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
weekday_num = now.weekday()
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day = days_of_week[weekday_num]
today = now.strftime('%Y-%m-%d %H:%M:%S')
days_in_current_month = calendar.monthrange(now.year, now.month)[1]
days_left_in_current_month = days_in_current_month - now.day
last_day_of_current_year = datetime.datetime(now.year, 12, 31, tzinfo=tz)
days_left_in_current_year = (last_day_of_current_year - now).days

list_goals_module_functions = {
    "name": "list_goals_module_functions",
    "description": "Lists functions in the Goals module",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing functions from the Goals module"]
            },
        },
        "required": []
    }
}

add_goal = {
  "name": "add_goal",
  "description": "Log a goal that the user wants to achieve",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "The name of the goal"
      },
      "date": {
        "type": "string",  
        "description": "The date by which the user wants to achieve the goal in YYYY-MM-DD format."
      },
      "today": {
        "type": "string",  
        "enum": [today]
      }
    },
    "required": ["event"]
  }
}

list_goals = {
    "name": "list_goals",
    "description": "Lists the user's goals",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing goals from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

update_goal_by_id = {
    "name": "update_goal_by_id",
    "description": "Update a goal by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Goal id"
            },
            "name": {
                "type": "string",
                "description": "The name of the goal"
            },
            "date": {
              "type": "string",
              "description": "The date by which the user wants to achieve the goal in YYYY-MM-DD format."
            },
        },
        "required": ["id"]
    }
}

delete_goals_by_ids = {
    "name": "delete_goals_by_ids",
    "description": "Delete goals by their ids",
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

add_reason = {
  "name": "add_reason",
  "description": "Log why a user wants to achieve a particular goal",
  "parameters": {
    "type": "object",
    "properties": {
      "goal_id": {
          "type": "integer",
          "description": "The id of the goal"
      },
      "reason": {
        "type": "string",
        "description": "The reason why the user wants to achieve that goal"
      },
    },
    "required": ["goal_id", "reason"]
  }
}

list_reasons_by_goal_id = {
    "name": "list_reasons_by_goal_id",
    "description": "List the reasons why the user wants to achieve a particular goal with a goal id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Goal id"
            },
        },
        "required": ["id"]
    }

}

update_reason_by_id = {
    "name": "update_reason_by_id",
    "description": "Update a reason by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Reason id"
            },
            "reason": {
                "type": "string",
                "description": "The name of the reason"
            },
        },
        "required": ["id", "reason"]
    }
}

delete_reasons_by_ids = {
    "name": "delete_reasons_by_ids",
    "description": "Delete reasons by their ids",
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

add_action = {
  "name": "add_action",
  "description": "Log actions a user will execute to achieve a particular goal",
  "parameters": {
    "type": "object",
    "properties": {
      "goal_id": {
          "type": "integer",
          "description": "The id of the goal"
      },
      "action": {
        "type": "string",
        "description": "The reason why the user wants to achieve that goal"
      },
      "deadline": {
        "type": "string", 
        "description": "The deadline by which the user will execute the action in YYYY-MM-DD format"
      },
      "today": {
        "type": "string", 
        "enum": [today]
      }
    },
    "required": ["goal_id", "action"]
  }
}

list_actions = {
    "name": "list_actions",
    "description": "Lists the actions the user will execute",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing actions from rgw-bot@GoogleCloudMySQL"]
            },
        },
        "required": []
    }
}

list_actions_by_goal_id = {
    "name": "list_actions_by_goal_id",
    "description": "List the actions the user will execute to achieve a particular goal with a goal id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Goal id"
            },
        },
        "required": ["id"]
    }

}

update_action_by_id = {
    "name": "update_action_by_id",
    "description": "Update an action by its id",
    "parameters": {
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "Action id"
            },
            "action": {
                "type": "string",
                "description": "The name of the action"
            },
            "deadline": {
              "type": "string", 
              "description": "The date by which the user wants to achieve the goal in YYYY-MM-DD format."
            },
        },
        "required": ["id"]
    }
}

delete_actions_by_ids = {
    "name": "delete_actions_by_ids",
    "description": "Delete actions by their ids",
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

add_timesheet_logs = {
  "name": "add_timesheet_logs",
  "description": "Log actions a user has taken on a particular day. User may indicate to mark actions with specific ids as done - in which case this function is also to be invoked",
  "parameters": {
    "type": "object",
    "properties": {
      "action_ids": {
          "type": "string",
          "description": "The ids of the actions taken separated by camel case. For instance ids 4 and 5 would be 4_5"
      },
      "date": {
        "type": "string", 
        "description": f"The date of the logs in YYYY-MM-DD format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
      },
      "today": {
        "type": "string", 
        "enum": [today]
      }
    },
    "required": ["action_ids"]
  }
}

list_timesheet_logs = {
  "name": "list_timesheet_logs",
  "description": "Lists logs of actions a user has taken on a particular day, or shows the user his timesheet for a particular day",
  "parameters": {
    "type": "object",
    "properties": {
      "date": {
        "type": "string", 
        "description": f"The date of the logs in YYYY-MM-DD format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
      },
      "today": {
        "type": "string", 
        "enum": [today]
      }
    },
    "required": ["action_ids"]
  }
}

delete_timesheet_logs = {
  "name": "delete_timesheet_logs",
  "description": "Deletes logs of actions a user has taken on a particular day. User may indicate to unmark actions with specific ids as done - in which case this function is also to be invoked",
  "parameters": {
    "type": "object",
    "properties": {
      "action_ids": {
          "type": "string",
          "description": "The ids of the actions taken separated by camel case. For instance ids 4 and 5 would be 4_5"
      },
      "date": {
        "type": "string", 
        "description": f"The date of the logs in YYYY-MM-DD format. Default is {today}. Otherwise, this needs to be calculated relative from {today}"
      },
      "today": {
        "type": "string",
        "enum": [today]
      }
    },
    "required": ["action_ids"]
  }
}

display_timesheets_line_chart = {
    "name": "display_timesheets_line_chart",
    "description": "Plots a line chart of the users timesheet entries over the given range of days",
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
                "description": "If the user has requested cumulative view. Default is false."
            },
            "today": {
                "type": "string",
                "enum": [today]
            }
        },
        "required": ["is_cumulative"]
    }
}







