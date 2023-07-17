import calendar
import datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d %H:%M:%S')


open_tweetpad = {
  "name": "open_tweetpad",
  "description": "Opens the user's tweet note in vim, also known as a tweetpad",
  "parameters": {
    "type": "object",
    "properties": {
      "tweetpad_id":{
        "type": "integer",
        "description": "the id of the user's tweet note",
       },
      "connection": {
        "type": "string",
        "enum": ["Opening tweetpad.txt"]
       },
     },
    "required": []
  }
}

save_tweetpads = {
  "name": "save_tweetpads",
  "description": "Saves all user's tweet notes in vim, also known as tweetpads",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Saving tweetpad.txt"]
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
      "connection": {
        "type": "string",
        "enum": ["Listing tweets"]
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

tweet = {
  "name": "tweet",
  "description": "Tweets the note prepared by the user",
  "parameters": {
    "type": "object",
    "properties": {
      "connection": {
        "type": "string",
        "enum": ["Tweeting"]
       },
       "today": {
         "type": "string",
         "enum": [today]
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








