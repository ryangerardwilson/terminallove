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

list_twitter_module_functions = {
    "name": "list_twitter_module_functions",
    "description": "Lists functions in the Twitter module",
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

list_twitter_rate_limits = {
    "name": "list_twitter_rate_limits",
    "description": "Lists Twitter rate limits",
    "parameters": {
        "type": "object",
        "properties": {
            "connection": {
                "type": "string",
                "enum": ["Listing Twitter rate limits"]
            },
        },
        "required": []
    }
}

list_tweets = {
  "name": "list_tweets",
  "description": "Lists the user's tweets",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of tweets to list out. Default is 10"
       },
     },
    "required": []
  }
}




