import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
import subprocess
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt
import time
from requests_oauthlib import OAuth1Session
import json
import pytz
import requests
import base64
import random

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
load_dotenv(os.path.join(parent_dir, '.env'))

OPEN_AI_API_KEY=os.getenv('OPEN_AI_API_KEY')

NOTE_IMAGE_STORAGE_BUCKET_NAME=os.getenv('NOTE_IMAGE_STORAGE_BUCKET_NAME')
GOOGLE_SERVICE_ACCOUNT_KEY=os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
path_to_service_account_file=os.path.join(parent_dir,'files/tokens/',GOOGLE_SERVICE_ACCOUNT_KEY)

TIMEZONE=os.getenv('TIMEZONE')
tz=pytz.timezone(TIMEZONE)

PUBLISHED_NOTE_SPACING=int(os.getenv('PUBLISHED_NOTE_SPACING'))

LINKEDIN_CLIENT_ID=os.getenv('LINKEDIN_CLIENT_ID')
LINKEDIN_CLIENT_SECRET=os.getenv('LINKEDIN_CLIENT_SECRET')
LINKEDIN_REDIRECT_URL=os.getenv('LINKEDIN_REDIRECT_URL')

TWITTER_AUTHENTICATION_KEY=os.getenv('TWITTER_AUTHENTICATION_KEY')
TWITTER_NOTE_SPACING=int(os.getenv('TWITTER_NOTE_SPACING'))
TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

conn = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE')
)

NOTE_TEXT_IMPROVISATION_CONCEPT_THEMES = [
    "Packet Switching",
    "Decentralization",
    "End-to-end principle",
    "TCP/IP Protocol",
    "Uniform Resource Locators",
    "Hypertext Transfer Protocol",
    "Domain Name Settings",
    "Open Standards and Interoperability",
    "Scalability",
    "Network Neutrality",
    "Redundancy",
    "Encapsulation",
    "Client-Server Model",
    "P2P networking",
    "Caching",
    "SSL/TLS",
    "Multiplexing",
    "IPv6",
    "Cookies",
    "Routing Protocols",
    "Firewalls",
    "Load Balancers",
    "Content Delivery Networks (CDNs)",
    "ICANN and IANA",
    "Public and Private IP Addresses",
    "VPNs",
    "APIs",
    "Responsive Web Design",
    "Deep and Dark Web",
    "Mesh Networks",
    "QoS Standards",
    "Zero Trust Security Model",
    "RESTful Web Services",
    "WebSockets",
    "Broadband and Fibre Optics",
    "IP4 Exhaustion and NAT",
    "Distributed Denial of Services (DDoS) Attacks",
    "Web Crawlers and Search Engines",
    "MPLS (Multi protocol label switching)"
    ]

NOTE_TEXT_IMPROVISATION_PROMPTS = [
    "explain the underlying philosophy of CONCEPT_THEME (in context of the internet) to first year philosohpy students, in the form of a story, in less than 300 words",
    "tell me a joke about CONCEPT_THEME",
    "give one example of any ancient philosopher's idea that is analogous to CONCEPT_THEME (in context of the internet), in less than 200 words",
    "give one example of any everyday task a puppy does that is analogous to CONCEPT_THEME (in context of the internet), in less than 200 words"
    ]

def publish_or_improvise_notes():

    error_logs = []
    cursor = conn.cursor()
    executed_at = datetime.datetime.now(tz)
    formatted_executed_at = executed_at.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO cronjob_logs (job_description, executed_at, error_logs) VALUES (%s, %s, %s)",
        ("Executing publishQueuedTweets.py", formatted_executed_at, json.dumps([]))
    )
        log_id = cursor.lastrowid
        conn.commit()

    def improvise_note():
        selected_theme = random.choice(NOTE_TEXT_IMPROVISATION_CONCEPT_THEMES)

        # Randomly select a prompt and embed the theme
        selected_prompt = random.choice(NOTE_TEXT_IMPROVISATION_PROMPTS)
        formatted_prompt = selected_prompt.replace("CONCEPT_THEME", selected_theme)

        # Store the final result in the variable randomized_prompt
        randomized_prompt = formatted_prompt

        print(randomized_prompt)
        return
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM (SELECT * FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 100) AS last_100_published_notes ORDER BY RAND() LIMIT 1"
    ¦   ¦   )
    ¦   ¦   random_note = cursor.fetchone()
    ¦   ¦   random_note_text = random_note[1]
    ¦   ¦   print('RANDOMLY SELECTED NOTE TEXT: ', random_note_text)
    ¦   ¦   print()
    ¦   ¦   print()
    ¦   ¦   prompt = f"Use vivid imagery and tell me a similar story, using fictional characters and short sentences: {random_note_text}"

    ¦   ¦   ai_generated_note_text = get_completion(prompt)
    ¦   ¦   print('bbb', ai_generated_note_text)
    ¦   ¦   print()
    ¦   ¦   print()

    ¦   ¦   formatted_text = reformat_text(ai_generated_note_text, 3)
    ¦   ¦   print('ccc', formatted_text)

    ¦   ¦   # Step 3 - Inset it into notes, and set the is_organic value of the note to false
    ¦   ¦   insert_cmd = (
    ¦   ¦   ¦   "INSERT INTO notes (note, is_published, created_at, updated_at, is_organic) "
    ¦   ¦   ¦   "VALUES (%s, %s, %s, %s, %s)"
    ¦   ¦   )
    ¦   ¦   is_published = False
    ¦   ¦   is_organic = False
    ¦   ¦   created_at = updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    ¦   ¦   cursor.execute(insert_cmd, (formatted_text, is_published, created_at, updated_at, is_organic))
    ¦   ¦   conn.commit()
    ¦   ¦   note_id = cursor.lastrowid




    try:

        # STEP 1: Check if there are any notes to publish for which SPACING has lapsed
        note_id = None
        query = "SELECT published_at FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            published_at = result[0]
            published_at = published_at.replace(tzinfo=tz)
            now = datetime.datetime.now(tz)
            hours_since_last_published_note = (now - published_at).total_seconds() / 3600
        else:
            hours_since_last_published_note = PUBLISHED_NOTE_SPACING + 1

        if (hours_since_last_published_note < PUBLISHED_NOTE_SPACING):
            return
        else:
            cursor.execute("SELECT note_id FROM spaced_publications ORDER BY note_id, id")
            result = cursor.fetchone()
            
            # STEP 2: Assign note_id to either the existing spaced publication or a newly improvised note
            if result is None:
                note_id = improvise_note()
            else:
                note_id = result[0]

        # STEP 3: Publish note_id
        if note_id != None:
            print(f"code to publish note id {note_id} to be executed")



    except Exception as e:
        error_logs.append(str(e))

    if error_logs == []:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s WHERE id = %s",
            ("Executed publishOrImproviseNotes.py", log_id)
            )
        conn.commit()
    else:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("Errors in executing publishQueuedTweets.py", json.dumps(error_logs), log_id)
            )
        conn.commit()


if __name__ == '__main__':
    publish_or_improvise_notes()


