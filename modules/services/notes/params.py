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

open_note = {
  "name": "open_note",
  "description": "Opens/creates a new note in vim, or opens/gets an existing note if an id is specified",
  "parameters": {
    "type": "object",
    "properties": {
      "id":{
        "type": "integer",
        "description": "the id of the user's note",
       },
     },
    "required": []
  }
}

open_most_recent_note = {
  "name": "open_most_recent_note",
  "description": "Opens the user's most recent note in vim",
  "parameters": {
    "type": "object",
    "properties": {
      "is_organic": {
        "type": "boolean",
        "description": "If user wants his organic note, then true. Else, false. Default is false."
       },
     },
    "required": []
  }
}


open_most_recently_edited_note = {
  "name": "open_most_recently_edited_note",
  "description": "Opens the user's most recently edited note in vim",
  "parameters": {
    "type": "object",
    "properties": {
      "is_organic": {
        "type": "boolean",
        "description": "If user wants his organic note, then true. Else, false. Default is false."
       },
     },
    "required": []
  }
}


save_and_close_notes = {
  "name": "save_and_close_notes",
  "description": "Saves the user's notes",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Syncing notes"]
       },
     },
    "required": []
  }
}

delete_local_note_cache = {
  "name": "delete_local_note_cache",
  "description": "Deletes local notes",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Deleting local note cache"]
       },
     },
    "required": []
  }
}

delete_notes_by_ids = {
    "name": "delete_notes_by_ids",
    "description": "Delete notes by their ids",
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

add_or_update_media_to_notes_by_ids = {
    "name": "add_or_update_media_to_notes_by_ids",
    "description": "Adds/updates/replaces media to notes by their ids",
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

list_notes = {
    "name": "list_notes",
    "description": "Lists the user's notes",
    "parameters": {
      "type": "object",
      "properties": {
        "limit": {
          "type": "integer",
          "description": "The number of notes to be listed"
          },
        "is_organic": {
          "type": "boolean",
          "description": "If user wants his organic note, then true. Else, false. Default is false."
           },
        },
        "required": []
    }
}

publish_notes_by_ids = {
    "name": "publish_notes_by_ids",
    "description": "Publish notes by their ids",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be published separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

unpublish_notes_by_ids = {
    "name": "unpublish_notes_by_ids",
    "description": "Unpublish notes by their ids",
    "parameters": {
        "type": "object",
        "properties": {
            "ids": {
                "type": "string",
                "description": "The ids to be unpublished separated by camel case. For instance ids 4 and 5 would be 4_5"
            },
        },
        "required": ["ids"]
    }
}

list_spaced_publications = {
  "name": "list_spaced_publications",
  "description": "Lists the user's scheduled publications, also known as spaced publications, spaced notes, queued publications, or queued notes",
  "parameters": {
    "type": "object",
    "properties": {
        "limit": {
        "type": "integer",
        "description": "The number of spaced publications to list out"
      },
     },
    "required": []
  }
}


