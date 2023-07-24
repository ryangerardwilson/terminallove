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

list_functions = {
    "name": "list_functions",
    "description": "Lists functions in the module",
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

list_rate_limits = {
    "name": "list_rate_limits",
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

list_queued_tweets = {
  "name": "list_queued_tweets",
  "description": "Lists the user's queued tweets",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of queued tweets to list out"
       },
     },
    "required": []
  }
}

list_spaced_tweets = {
  "name": "list_spaced_tweets",
  "description": "Lists the user's scheduled tweets, also known as spaced tweets",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of spaced tweets to list out"
       },
     },
    "required": []
  }
}

tweet_out_note = {
  "name": "tweet_out_note",
  "description": "Tweets the note prepared by the user by its id",
  "parameters": {
    "type": "object",
    "properties": {
      "id": {
        "type": "integer",
        "description": "The id of the note"
       },
     },
    "required": []
  }
}

schedule_tweet = {
  "name": "schedule_tweet",
  "description": "Schedules the tweeting of the note prepared by the user to a late date",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Scheduling tweet"]
       },
      "today": {
         "type": "string",
         "enum": [today]
       },
     },
    "required": []
  }
}

edit_tweet = {
  "name": "edit_tweet",
  "description": "Edits the user's tweet",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Editing tweet"]
       },
      "today": {
         "type": "string",
         "enum": [today]
       },
     },
    "required": []
  }
}

delete_tweets_by_ids = {
  "name": "delete_tweets_by_ids",
  "description": "Deletes tweets by their ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}


delete_tweets_by_note_ids = {
  "name": "delete_tweets_by_note_ids",
  "description": "Deletes tweets by their note ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}

delete_queued_tweets_by_ids = {
  "name": "delete_queued_tweets_by_ids",
  "description": "Deletes queued tweets by their ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}


delete_queued_tweets_by_note_ids = {
  "name": "delete_queued_tweets_by_note_ids",
  "description": "Deletes queued tweets by their note ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}

delete_spaced_tweets_by_ids = {
  "name": "delete_spaced_tweets_by_ids",
  "description": "Deletes spaced/ scheduled tweets by their ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}


delete_spaced_tweets_by_note_ids = {
  "name": "delete_spaced_tweets_by_note_ids",
  "description": "Deletes spaced/ scheduled tweets by their note ids",
  "parameters": {
    "type": "object",
    "properties": {
        "ids": {
            "type": "string",
            "description": "The ids to be deleted separated by camel case. For instance ids 4 and 5 would be 4_5"
        },
     },
    "required": []
  }
}








