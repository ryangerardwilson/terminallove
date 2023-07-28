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

list_rate_limits = {
    "name": "list_rate_limits",
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

list_queued_linkedin_posts = {
  "name": "list_queued_linkedin_posts",
  "description": "Lists the user's queued LinkedIn posts",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of queued LinkedIn posts to list out"
       },
     },
    "required": []
  }
}

list_spaced_linkedin_posts = {
  "name": "list_spaced_linkedin_posts",
  "description": "Lists the user's scheduled LinkedIn posts, also known as spaced LinkedIn posts",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of spaced LinkedIn posts to list out"
       },
     },
    "required": []
  }
}

linkedin_post_out_note = {
  "name": "linkedin_post_out_note",
  "description": "Posts to LinkedIn the note prepared by the user by its id",
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

schedule_linkedin_post = {
  "name": "schedule_linkedin_post",
  "description": "Schedules the LinkedIn posting of the note prepared by the user to a late date",
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

delete_linkedin_posts_by_ids = {
  "name": "delete_linkedin_posts_by_ids",
  "description": "Deletes LinkedIn posts by their ids",
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

delete_linkedin_posts_by_note_ids = {
  "name": "delete_linkedin_posts_by_note_ids",
  "description": "Deletes LinkedIn posts by their note ids",
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

delete_queued_linkedin_posts_by_ids = {
  "name": "delete_queued_linkedin_posts_by_ids",
  "description": "Deletes queued LinkedIn posts by their ids",
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


delete_queued_linkedin_posts_by_note_ids = {
  "name": "delete_queued_linkedin_posts_by_note_ids",
  "description": "Deletes queued LinkedIn posts by their note ids",
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

delete_spaced_linkedin_posts_by_ids = {
  "name": "delete_spaced_linkedin_posts_by_ids",
  "description": "Deletes spaced/ scheduled LinkedIn posts by their ids",
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


delete_spaced_linkedin_posts_by_note_ids = {
  "name": "delete_spaced_linkedin_posts_by_note_ids",
  "description": "Deletes spaced/ scheduled LinkedIn posts by their note ids",
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








