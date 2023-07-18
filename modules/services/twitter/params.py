import calendar
import datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')


list_tweets = {
  "name": "list_tweets",
  "description": "Lists the user's tweets",
  "parameters": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "The number of tweets to list out"
       },
     },
    "required": []
  }
}

list_scheduled_tweets = {
  "name": "list_scheduled_tweets",
  "description": "Lists the user's scheduled tweets",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Listing scheduled tweets"]
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
  "description": "Schedule the tweet the note prepared by the user to be tweeted on a late date",
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








