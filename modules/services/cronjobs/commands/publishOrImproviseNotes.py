import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
import re
import textwrap
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
GPT_MODEL=os.getenv('GPT_MODEL')

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
        def improvise_note_text_from_themes():
            selected_theme = random.choice(NOTE_TEXT_IMPROVISATION_CONCEPT_THEMES)
            # Randomly select a prompt and embed the theme
            selected_prompt = random.choice(NOTE_TEXT_IMPROVISATION_PROMPTS)
            formatted_prompt = selected_prompt.replace("CONCEPT_THEME", selected_theme)

            # Store the final result in the variable randomized_prompt
            randomized_prompt = formatted_prompt
            return randomized_prompt

        def improvise_note_text_from_previous_organic_notes():
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM ("
                "    SELECT * FROM ("
                "        SELECT * FROM notes "
                "        WHERE is_published = 1 AND is_organic = 1 "
                "        ORDER BY published_at DESC "
                "        LIMIT 105"
                "    ) AS last_105_published_notes "
                "    ORDER BY published_at ASC "
                "    LIMIT 100"
                ") AS filtered_notes "
                "ORDER BY RAND() "
                "LIMIT 1"
            )
            random_note = cursor.fetchone()
            random_note_text = random_note[1]
            randomized_prompt = f"Paraphrase this in less than 200 words: {random_note_text}"
            return randomized_prompt

        def get_completion(prompt):
            url = "https://api.openai.com/v1/chat/completions"
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPEN_AI_API_KEY}",
            }
            data = {
                "model": GPT_MODEL,
                "messages": messages,
            }
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:  # Check if the request was successful
                response_content = response.json()
                assistant_message = response_content['choices'][0]['message']['content']
                return assistant_message  # Returns the content of the assistant's message
            else:
                return None

        def format_text(text):
            # Remove existing paragraph numbering
            text = re.sub(r'\{\d+/\d+\} ', '', text)
            # Combine all text into one paragraph
            combined_text = text.replace("\n\n", " ").replace("\n", " ")

            # Split the combined text into sentences
            sentences = re.split(r'\. |\? ', combined_text)

            # Add the '.' or '?' back into each sentence except for the last one
            sentences = [sentence + ('.' if not sentence.endswith('?') else '?') for sentence in sentences[:-1]] + [sentences[-1]]

            # Combine sentences into new paragraphs of less than 280 characters
            formatted_paragraphs = []
            current_paragraph = ""
            for sentence in sentences:
                if len(current_paragraph) + len(sentence) > 270:  # +10 for prefix
                    formatted_paragraphs.append(current_paragraph.strip())
                    current_paragraph = sentence
                else:
                    current_paragraph += " " + sentence

            # Don't forget the last paragraph   
            if current_paragraph:
                formatted_paragraphs.append(current_paragraph.strip())
            
            min_paragraphs = 3

            # If not enough paragraphs, split the longest one
            while len(formatted_paragraphs) < min_paragraphs:
                max_len_idx = max(range(len(formatted_paragraphs)), key=lambda index: len(formatted_paragraphs[index]))
                long_paragraph = formatted_paragraphs.pop(max_len_idx)
                half = len(long_paragraph) // 2
                first_half = long_paragraph[:half].rsplit('. ', 1)[0] + '.'
                second_half = long_paragraph[half:].lstrip()
                formatted_paragraphs.extend([first_half, second_half])

            result = '\n\n'.join(formatted_paragraphs)
            return result


        # Decide which function to call based on the probability
        if random.random() < 0.6:
            prompt = improvise_note_text_from_previous_organic_notes()
        else:
            prompt = improvise_note_text_from_themes()

        ai_generated_note_text = get_completion(prompt)
        print('218', ai_generated_note_text)
        if ai_generated_note_text != None:
            formatted_text = format_text(ai_generated_note_text)

            insert_cmd = (
                "INSERT INTO notes (note, is_published, is_organic, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s)"
                )
            is_organic = False
            is_published = False
            created_at = updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(insert_cmd, (formatted_text, is_published, is_organic, created_at, updated_at))
            conn.commit()
            new_id = cursor.lastrowid
            return new_id
        else:
            return None



        """

        ai_generated_note_text = get_completion(prompt)
        print('bbb', ai_generated_note_text)
        print()
        print()

        formatted_text = reformat_text(ai_generated_note_text, 3)
        print('ccc', formatted_text)

        # Step 3 - Inset it into notes, and set the is_organic value of the note to false
        insert_cmd = (
            "INSERT INTO notes (note, is_published, created_at, updated_at, is_organic) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        is_published = False
        is_organic = False
        created_at = updated_at = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(insert_cmd, (formatted_text, is_published, created_at, updated_at, is_organic))
        conn.commit()
        note_id = cursor.lastrowid

        """


    try:

        # STEP 1: Check if there are any notes to publish for which SPACING has lapsed
        note_id = None
        query = "SELECT published_at FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchall()
        print('168', result)
        if result:
            published_at = result[0][0]
            print('171', published_at)
            print('Is datetime:', isinstance(published_at, datetime.datetime))
            print('Timezone-aware:', published_at.tzinfo is not None)
            published_at = published_at.replace(tzinfo=tz)
            print('172', published_at)
            now = datetime.datetime.now(tz)
            hours_since_last_published_note = (now - published_at).total_seconds() / 3600
        else:
            hours_since_last_published_note = PUBLISHED_NOTE_SPACING + 1

        print('177', hours_since_last_published_note)

        if (hours_since_last_published_note < PUBLISHED_NOTE_SPACING):
            print('Too soon to publish')
            return
        else:
            cursor.execute("SELECT note_id FROM spaced_publications ORDER BY id")
            result = cursor.fetchall()
            print('183', result)
            # STEP 2: Assign note_id to either the existing spaced publication or a newly improvised note
            if result is None:
                print('184')
                note_id = improvise_note()
            else:
                note_id = result[0][0]

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


