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

list_linkedin_module_functions = {
    "name": "list_linkedin_module_functions",
    "description": "Lists functions in the LinkedIn module",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing functions from LinkedIn module"]
            },
        },
        "required": []
    }
}

list_linkedin_rate_limits = {
    "name": "list_linkedin_rate_limits",
    "description": "Lists LinkedIn rate limits",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing LinkedIn rate limits"]
            },
        },
        "required": []
    }
}

list_linkedin_posts = {
  "name": "list_linkedin_posts",
  "description": "Lists the user's LinkedIn posts",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of LinkedIn posts to list out. Default is 10"
       },
     },
    "required": []
  }
}




