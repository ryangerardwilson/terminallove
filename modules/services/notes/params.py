import calendar
import datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')


open_note = {
  "name": "open_note",
  "description": "Creates a new note and opens it in vim, or opens an existing on if an id is specified",
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
      "connection": {
        "type": "string",
        "enum": ["Opening most recent note"]
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
      "connection": {
        "type": "string",
        "enum": ["Opening most recently edited note"]
       },
     },
    "required": []
  }
}


save_and_close_notes = {
  "name": "save_and_close_notes",
  "description": "Saves all user's notes in vim",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Saving notes"]
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
        },
        "required": []
    }
}






