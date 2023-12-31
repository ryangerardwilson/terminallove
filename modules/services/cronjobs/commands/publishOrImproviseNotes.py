import mysql.connector
import datetime
import pandas as pd
from termcolor import colored
import os
import io
import re
import textwrap
import subprocess
from tabulate import tabulate
from dotenv import load_dotenv
import plotext as plt
import time
from requests_oauthlib import OAuth1Session
from google.cloud import storage
import urllib.parse
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

MEDIA_IMPROVISATION_PROMPTS = [
    "Steampunk-inspired illustration, containing cyborgs, with a strong black aura, representing this theme: FIRST_PARAGRAPH",
    "Digital illustration, containing cyborgs, with a strong black aura, representing this theme: FIRST_PARAGRAPH",
    ]  

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

SENTENCE_START_PROMPTS = [
    "This guy created...",
    "Hear that?",
    "This is our chance to",
    "Good riddance",
    "Another big step towards",
    "Can we put an end to",
    "Who will pay to",
    "The end of",
    "Move aside",
    "Once science fiction",
    "Is it finally hammer time",
    "The unexpected joys of",
    "The epic battle between",
    "In the heart of",
    "The shaky future of",
    "Why are you",
    "Be paranoid about",
    "There is a reason",
    "Why can't we stop",
    "Why do we tolerate",
    "Whatever you think of",
    "There is a lot we still don't know about",
    "Why it's important that",
    "We shouldn't be scared by",
    "Was that the best",
    "The black and white world of",
    "Everyone is dead",
    "What happens when",
    "The twilight of",
    "Why you shouln't believe",
    "The loophole",
    "There is no",
    "Who killed",
    "The trauma of",
    "Not everyone wanted",
    "The high price of",
    "The rise and fall of",
    "Welcome to the",
    "The worm that nearly ate",
    "What if we all just",
    "You care more about",
    "The people screaming for blood have no idea",
    "Why should we stop fetishizing",
    "It's time to break up",
    "The devastating consequences of",
    "It's time to panic",
    "Where would you draw the line",
    "You are not as good at",
    "Why the cool kids are",
    "The joy of standards",
    "We should be able to take",
    "Is this the end of",
    "A smarter way to think about",
    ]

NOTE_TEXT_IMPROVISATION_PROMPTS = [
    "explain the underlying philosophy of CONCEPT_THEME (in context of the internet) to first year philosohpy students, in less than 300 words. Start your response with - SENTENCE_START_PROMPTS",
    "give one example of any ancient philosopher's idea that is analogous to CONCEPT_THEME (in context of the internet), in less than 200 words. Start your response with - SENTENCE_START_PROMPTS",
    ]

def publish_or_improvise_notes():

    error_logs = []
    execution_logs = []
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
            selected_sentence_start_prompt = random.choice(SENTENCE_START_PROMPTS)
            formatted_prompt = selected_prompt.replace("CONCEPT_THEME", selected_theme).replace("SENTENCE_START_PROMPT", selected_sentence_start_prompt)
            

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
                if len(current_paragraph) + len(sentence) > 250:  # +10 for prefix
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
        # if random.random() < 0.6:
            # prompt = improvise_note_text_from_previous_organic_notes()
        # else:
            # prompt = improvise_note_text_from_themes()
        
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

    try:

        # STEP 1: Check if there are any notes to publish for which SPACING has lapsed
        note_id = None
        query = "SELECT published_at FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchall()
        execution_logs.append('310')
        print('Line: 310')
        if result:
            published_at = result[0][0]
            published_at = published_at.replace(tzinfo=tz)
            execution_logs.append('315')
            print('Line: 315')
            now = datetime.datetime.now(tz)
            hours_since_last_published_note = (now - published_at).total_seconds() / 3600
        else:
            hours_since_last_published_note = PUBLISHED_NOTE_SPACING + 1

        execution_logs.append('322')
        print('Line: 322')

        was_note_improvised = False
        if (hours_since_last_published_note < PUBLISHED_NOTE_SPACING):
            print('Too soon to publish')
            execution_logs.append('328')
            print('Line: 328')
            return
        else:
            cursor.execute("SELECT note_id FROM spaced_publications ORDER BY id")
            result = cursor.fetchall()
            execution_logs.append('334')
            print('Line: 334')
            # STEP 2: Assign note_id to either the existing spaced publication or a newly improvised note
            if result == []:
                execution_logs.append('338')
                print('Line: 338')
                note_id = improvise_note()
                was_note_improvised = True
            else:
                note_id = result[0][0]

        # STEP 3: Publish note_id
        if note_id != None:
            execution_logs.append('347')
            print('Line: 347')

            fn_publish_notes_by_ids(note_id, error_logs, execution_logs, log_id)

            # STEP 4: If note was published, make sure that it is deleted from spaced_publications
            check_published_query = "SELECT COUNT(*) FROM notes WHERE id = %s AND is_published = 1"
            cursor.execute(check_published_query, (note_id,))
            is_published_count = cursor.fetchone()[0]
            if is_published_count > 0:
                delete_query = "DELETE FROM spaced_publications WHERE note_id = %s"
                cursor.execute(delete_query, (note_id,))
                print(f"Deleted note id {note_id} from spaced_publications because it was published.")
                execution_logs.append('360')
                print('Line: 360')
                conn.commit()

            # STEP 5: If not was improvised, but not properly published, then unpublish the note and delete the note itself
            if is_published_count == 0 and was_note_improvised == True:
                fn_unpublish_note(note_id)
                delete_query = "DELETE FROM notes WHERE id = %s"
                cursor.execute(delete_query, (note_id,))
                print(f"Deleted note id {note_id} from notes because it was improvised but could not be published")
                conn.commit()
                execution_logs.append('370')
                print('Line: 370')

    except Exception as e:
        print(e)
        error_logs.append(str(e))

    if error_logs == []:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, execution_logs = %s WHERE id = %s",
            ("Executed publishOrImproviseNotes.py", json.dumps(execution_logs), log_id)
            )
        conn.commit()
    else:
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, execution_logs = %s, error_logs = %s WHERE id = %s",
            ("Errors in executing publishOrImproviseNotes.py", json.dumps(execution_logs), json.dumps(error_logs), log_id)
            )
        conn.commit()

    
def fn_publish_notes_by_ids(note_id, error_logs, execution_logs, log_id):

    cursor = conn.cursor()
    def generate_media_for_note(note_id):
        try:
            select_cmd = (
                "SELECT note FROM notes WHERE id = %s"
            )
            cursor.execute(select_cmd, (note_id,))
            execution_logs.append('400')

            row = cursor.fetchone()
            if row:
                note_text, = row
            else:
                print(f"No note found for note_id {note_id}")
                return False

            paragraphs = note_text.split("\n\n")
            first_paragraph = paragraphs[0]

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPEN_AI_API_KEY}"
            }
            data = {
                "prompt": f"Eerie painting in a dimly lit room, using shadows and low-light techniques representing this theme: {first_paragraph}",
                "n": 1,
                "size": "512x512"
            }
            execution_logs.append('421')
            response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=json.dumps(data))
            response_data = response.json()
            execution_logs.append('424')
            open_ai_media_url = response_data['data'][0]['url']
            downloaded_image = requests.get(open_ai_media_url)

            if downloaded_image.status_code != 200:
                execution_logs.append('429')
                raise Exception("Failed to download image from URL: {} {}".format(downloaded_image.status_code, downloaded_image.text))

            image_content = downloaded_image.content

            # Upload the media to Google Cloud Storage
            storage_client = storage.Client.from_service_account_json(path_to_service_account_file)
            bucket = storage_client.get_bucket(NOTE_IMAGE_STORAGE_BUCKET_NAME)

            filename = f"{note_id}_{datetime.datetime.now(tz).strftime('%Y%m%d_%H%M%S')}"

            blob = bucket.blob(f"{filename}.jpg")
            blob.upload_from_string(
                image_content,
                content_type='image/jpeg'
            )
            execution_logs.append('445')

            # Access the image URL and media ID
            media_url = blob.public_url
            update_cmd = ("UPDATE notes SET media_url = %s WHERE id = %s")
            cursor.execute(update_cmd, (media_url, note_id))
            conn.commit()
            return True
        except Exception as e:
            print(colored(f"FAILED TO GENERATE MEDIA FOR NOTE {note_id}: ","cyan"), e)
            error_logs.append("FAILED TO GENERATE MEDIA FOR NOTE")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s, execution_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), json.dumps(execution_logs), log_id)
            )
            conn.commit()
            return False

    def tweet_out_note(note_id):
        try:
            inserted_tweets = []
            media_url = None
            media_id = None
            execution_logs.append('469')

            select_cmd = ("SELECT note, media_url FROM notes WHERE id = %s")
            cursor.execute(select_cmd, (note_id,))
            note_result = cursor.fetchone()
            note_text, media_url = note_result

            previous_tweet_id = None

            if note_text == None:
                print(colored("You can't tweet an empty note", 'red'))
                return False

            cursor.execute("SELECT tweet FROM tweets")
            previous_tweets = {row[0] for row in cursor.fetchall()}
            execution_logs.append('484')
            paragraphs = note_text.split("\n\n")

            for i, paragraph in enumerate(paragraphs, 1):
                execution_logs.append('488')
                if not paragraph.strip():
                    print(colored(f"Skipping empty paragraph {i}", 'red'))
                    if i == 1:
                        print(colored('You may have forgotten to save the note', 'red'))
                    continue

                if len(paragraph) > 280:
                    print(colored(f"Paragraph {i} is longer than 280 characters by {len(paragraph) - 280} characters. Not tweeting anything", 'red'))
                    delete_query = "DELETE FROM spaced_publications WHERE note_id = %s"
                    cursor.execute(delete_query, (note_id,))
                    print(f"Deleted note id {note_id} from spaced_publications because it was improvised but contains a para that exceeds 280 characters")
                    execution_logs.append('500')
                    print('Line: 500')
                    fn_unpublish_note(note_id)
                    print('deleted any published remnants of the note')
                    execution_logs.append('505')
                    conn.commit()
                    return False

                if paragraph in previous_tweets:
                    print(colored(f"Paragraph {i} has already been posted. Not tweeting anything", 'red'))
                    return False

                payload = {"text": paragraph}
     
                if previous_tweet_id is not None:
                    payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}
     
                time.sleep(1)
                oauth = get_oauth_session()

                if i == 1 and media_url != None:
                    media_id = get_media_id_after_uploading_image_to_twitter(media_url)

                if i == 1 and media_id != 0:
                    payload["media"] = {"media_ids": [media_id]}
                else:
                    media_url = None
                    media_id = None

                response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
                execution_logs.append('521')
                if response.status_code != 201:
                    execution_logs.append('523')
                    delete_tweets_by_note_id(note_id)
                    print(colored(f"Request returned an error with status code {response.status_code}", "cyan"))
                    return False

                json_response = response.json()

                if 'data' in json_response:
                    execution_logs.append('531')
                    tweet_id = json_response['data']['id']
                    previous_tweet_id = tweet_id
                    posted_at = datetime.datetime.now(tz)
                    insert_cmd = ("INSERT INTO tweets (tweet, tweet_id, posted_at, note_id, media_id) VALUES (%s, %s, %s, %s, %s)")
                    cursor.execute(insert_cmd, (paragraph, tweet_id, posted_at, note_id, media_id))
                    conn.commit()

                    inserted_tweets.append({
                        'para': i,
                        'tweet': paragraph,
                        'tweet_id': tweet_id,
                        'posted_at': posted_at,
                        'note_id': note_id,
                        'media_id':media_id,
                    })

            if inserted_tweets:
                df = pd.DataFrame(inserted_tweets)
                df['tweet'] = df['tweet'].apply(lambda x: (x[:30] + '....') if len(x) > 30 else x)
                print(colored("\nSuccessfully tweeted out note id {note_id}\n", "cyan"))
                print(colored(tabulate(df, headers='keys', tablefmt='psql', showindex=False), 'cyan'))
                return True
     
        except Exception as e:
            execution_logs.append('556')
            print(colored(f"Failed to tweet out note id {note_id}: ","cyan"), e)
            error_logs.append("FAILED TO TWEET OUT NOTE")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
            )
            conn.commit()
            return False

    def delete_tweets_by_note_id(note_id):
        try:
            select_cmd = "SELECT id, tweet_id FROM tweets WHERE note_id = %s"
            cursor.execute(select_cmd, (note_id,))
            results = cursor.fetchall()
            if not results:
                print(colored(f"No published tweets to delete for note id {note_id}", 'cyan'))
            else:
                oauth = get_oauth_session()
                for result in results:
                    table_id, tweet_id = result
                    time.sleep(1)
                    # Delete the tweet on Twitter
                    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                    response = oauth.delete(url)
                    # Check for a successful response
                    if response.status_code == 200:
                    # If the deletion was successful on Twitter, delete the record from the tweets table
                        sql = "DELETE FROM tweets WHERE id = %s"
                        cursor.execute(sql, (table_id,))
                    else:
                        print(colored(f"Failed to delete tweet with {tweet_id} for note id {note_id}", 'cyan'))
                        print(response.text)
        except Exception as e:
            print(e)
            error_logs.append("FAILED TO DELETE TWEETS")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
            )
            conn.commit()


    def post_note_to_linkedin(note_id):
        try:
            select_cmd = ("SELECT note, media_url FROM notes WHERE id = %s")
            cursor.execute(select_cmd, (note_id,))
            note_result = cursor.fetchone()
            note_text, media_url = note_result
            access_token, linkedin_id = get_active_access_token_and_linkedin_id()
            if note_text == None:
                print(colored("You can't post an empty note", 'red'))
                return False

            cursor.execute("SELECT post FROM linkedin_posts")
            previous_published_posts = {row[0] for row in cursor.fetchall()}

            if not note_text.strip():
                print(colored(f"Note is empty, and, therefore, not posted. You may have forgotten to save the note", "cyan"))
                return False

            if note_text in previous_published_posts:
                print(colored(f"Note id {i} has already been posted to linkedin. Not posting anything to linkedin", 'red'))
                return False
            media_asset_urn = get_asset_urn_after_uploading_image_to_linkedin(media_url)

            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            data = {
                "author": f"urn:li:person:{linkedin_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": note_text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Center stage!"
                                },
                                "media": media_asset_urn,
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, data=json.dumps(data))

            if response.status_code != 201:
                delete_linkedin_posts_by_note_id(note_id)
                print(colored(f"Request returned an error with status code {response.status_code}", "cyan"))
                print(colored(response.text, "cyan"))
                return False
            else:
                json_response = response.json()
                print('700')
                post_id = response.headers.get('X-RestLi-Id')
                posted_at = datetime.datetime.now(tz)
                insert_cmd = ("INSERT INTO linkedin_posts (post, post_id, posted_at, note_id, media_asset_urn) VALUES (%s, %s, %s, %s, %s)")
                cursor.execute(insert_cmd, (note_text, post_id, posted_at, note_id, media_asset_urn))
                conn.commit()
                return True
        except Exception as e:
            print(colored(f"FAILED TO POST NOTE ID {note_id} TO LINKEDIN","cyan"), e)
            error_logs.append("FAILED TO POST NOTE TO LINKEDIN")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
            )
            conn.commit()
            return False

    def delete_linkedin_post_by_note_id(note_id):
        try:
            select_cmd = "SELECT id, note_id, post_id FROM linkedin_posts WHERE note_id = %s"
            cursor.execute(select_cmd, (note_id,))
            result = cursor.fetchone()
            if not result:
                print(colored(f"No published linkedin posts to delete for note id {note_id}", 'cyan'))
            else:
                table_id, note_id, post_id = result
                time.sleep(1)
                url = f"https://api.linkedin.com/v2/ugcPosts/{post_id}"

                access_token, linkedin_id = get_active_access_token_and_linkedin_id()

                headers = {
                    'Authorization': 'Bearer ' + access_token,
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
                response = requests.delete(url, headers=headers)

                if response.status_code == 200:
                    # If the deletion was successful, delete the record from the tweets table
                    sql = "DELETE FROM linkedin_posts WHERE id = %s"
                    cursor.execute(sql, (table_id,))

                if response.status_code != 200:
                    print('726')
                    print(colored(f"Request returned an error with status code {response.status_code}", "cyan"))
                    print(colored(response.text, "cyan"))
                    return False
                else:
                    print(f"Deleted note id {note_id} from LinkedIn")
        except Exception as e:
            print(e)
            error_logs.append("FAILED TO DELETE NOTE FROM LINKEDIN")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
            )
            conn.commit()
            return False

    def set_is_published_to_true(note_id):
        try:
            published_at = datetime.datetime.now(tz)
            print(colored(f"Setting note id {note_id} as published", "cyan"))
            update_cmd = ("UPDATE notes SET is_published = 1, published_at = %s WHERE id = %s")
            cursor.execute(update_cmd, (published_at, note_id,))
            conn.commit()
            return True
        except Exception as e:
            print(e)
            error_logs.append("FAILED TO SET IS PUBLISHED TO TRUE")
            error_logs.append(str(e))
            cursor.execute(
                "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
                ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
            )
            conn.commit()
            return False

    cursor.execute("SELECT media_url FROM notes WHERE id = %s", (note_id,))
    result = cursor.fetchone()

    if result:
        media_url, = result
    else:
        media_url = None 


    try:
        # SQL query to fetch the most recent published note
        query = "SELECT published_at FROM notes WHERE is_published = 1 ORDER BY published_at DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        print('736')
        if result:
            published_at = result[0]
            published_at = published_at.replace(tzinfo=tz)
            now = datetime.datetime.now(tz)
            hours_since_last_published_note = (now - published_at).total_seconds() / 3600
        else:
            hours_since_last_published_note = PUBLISHED_NOTE_SPACING + 1
        if (hours_since_last_published_note < PUBLISHED_NOTE_SPACING):
            cursor.execute("SELECT COUNT(*) FROM spaced_publications")
            count = cursor.fetchone()[0]
            x = count + 1
            cursor.execute("INSERT INTO spaced_publications (note_id) VALUES (%s)", (note_id,))
            conn.commit()
            print(colored(f"Note id {note_id} has been spaced out, and will be published {x} in line", 'cyan'))
            return
        print('752')
        has_media = False
        if media_url == None:
            has_media = generate_media_for_note(note_id)
        else:
            has_media = True
        print("LEG 1 SUCCESSFUL")

        all_tweets_related_to_note_published = False
        if has_media == True:
            print('771')
            all_tweets_related_to_note_published = tweet_out_note(note_id)
            note_posted_to_linkedin = False
            print('774')
            if all_tweets_related_to_note_published == True:
                print("LEG 2 SUCCESSFUL")
                note_posted_to_linkedin = post_note_to_linkedin(note_id)

        if all_tweets_related_to_note_published == False or note_posted_to_linkedin == False:
            # first check if note_id already exists in spaced_publications
            cursor.execute("SELECT EXISTS(SELECT 1 FROM spaced_publications WHERE note_id=%s)", (note_id,))
            if cursor.fetchone()[0]:  # it will return True if exists
                print(f"note_id {note_id} already exists in spaced_publications.")
            else:
                queue_insert_cmd = ("INSERT INTO spaced_publications (note_id) VALUES (%s)")
                cursor.execute(queue_insert_cmd, (note_id,))
                conn.commit()

        if has_media == True and all_tweets_related_to_note_published == True and note_posted_to_linkedin == True:
            set_is_published_to_true(note_id)
            print(colored(f"Note id {note_id} successfully published", "cyan"))

    except Exception as e:
        print('line 686 error ', e)
        error_logs.append("FINAL STEP EXCEPTION THROWN")
        error_logs.append(str(e))
        cursor.execute(
            "UPDATE cronjob_logs SET job_description = %s, error_logs = %s WHERE id = %s",
            ("Errors in executing publishOrImproviseNotes.py", json.dumps(error_logs), log_id)
        )
        conn.commit()

    return


def get_oauth_session():

    oauth = OAuth1Session(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET,
    )

    response = oauth.post("https://api.twitter.com/2/tweets")
    if response.status_code != 201:
        # Load existing tokens from file, if available
        tokens_file = f"{parent_dir}/files/tokens/{TWITTER_AUTHENTICATION_KEY}"
        try:
            with open(tokens_file, 'r') as f:
                tokens = json.load(f)
            access_token = tokens['access_token']
            access_token_secret = tokens['access_token_secret']
        except FileNotFoundError:
            # Get new tokens and save them to file
            request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
            oauth = OAuth1Session(TWITTER_CONSUMER_KEY, client_secret=TWITTER_CONSUMER_SECRET)
            try:
                fetch_response = oauth.fetch_request_token(request_token_url)
            except ValueError:
                print("There may have been an issue with the consumer_key or consumer_secret you entered.")
            resource_owner_key = fetch_response.get("oauth_token")
            resource_owner_secret = fetch_response.get("oauth_token_secret")
            print("Got OAuth token: %s" % resource_owner_key)
            base_authorization_url = "https://api.twitter.com/oauth/authorize"
            authorization_url = oauth.authorization_url(base_authorization_url)
            print("Please go here and authorize: %s" % authorization_url)
            verifier = input("Paste the PIN here: ")
            access_token_url = "https://api.twitter.com/oauth/access_token"
            oauth = OAuth1Session(
                TWITTER_CONSUMER_KEY,
                client_secret=TWITTER_CONSUMER_SECRET,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                verifier=verifier,
            )
            oauth_tokens = oauth.fetch_access_token(access_token_url)
            access_token = oauth_tokens["oauth_token"]
            access_token_secret = oauth_tokens["oauth_token_secret"]
            # Save tokens to file
            with open(tokens_file, 'w') as f:
                json.dump({'access_token': access_token, 'access_token_secret': access_token_secret}, f)
        # Use the tokens for the API call
        oauth = OAuth1Session(
            TWITTER_CONSUMER_KEY,
            client_secret=TWITTER_CONSUMER_SECRET,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

    return oauth

def get_media_id_after_uploading_image_to_twitter(media_url):

    # Download the image from the URL
    downloaded_image = requests.get(media_url)

    if downloaded_image.status_code != 200:
        raise Exception("Failed to download image from URL: {} {}".format(downloaded_image.status_code, downloaded_image.text))

    image_content = downloaded_image.content
    base64_image_content = base64.b64encode(image_content).decode('utf-8')

    # Upload the media to Twitter
    media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"

    oauth = get_oauth_session()
    image_upload_response = oauth.post(media_upload_url, data={"media_data": base64_image_content})

    if image_upload_response.status_code == 200:
        json_image_upload_response = image_upload_response.json()
        print(json_image_upload_response)
        media_id = json_image_upload_response["media_id_string"]
    else:
        print(colored('Image upload to twitter failed','red'))
        media_id = 0

    return media_id


def get_active_access_token_and_linkedin_id():

    def get_access_code_from_db():
        cursor = conn.cursor()

        cursor.execute("SELECT access_code FROM linkedin_access_codes ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()

        return row[0] if row else None

    def generate_new_access_code():
        url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={LINKEDIN_CLIENT_ID}&redirect_uri={LINKEDIN_REDIRECT_URL}&state=foobar&scope=r_liteprofile%20r_emailaddress%20w_member_social"
        print(colored("Click here to generate new access code: " + url, 'cyan'))

        user_input = input("Have you authorized the new access code? (yes/no): ")

        if user_input.lower() != 'yes':
            print("Please authorize the new access code before proceeding.")
            return None

        new_access_code = get_access_code_from_db()

        if new_access_code is None:
            print("No access code found in the database. Please try again.")
            return None

        return new_access_code

    def generate_new_access_token(access_code):
        data = {
            'grant_type': 'authorization_code',
            'code': access_code,
            'client_id': LINKEDIN_CLIENT_ID,
            'client_secret': LINKEDIN_CLIENT_SECRET,
            'redirect_uri': LINKEDIN_REDIRECT_URL
        }
        response = requests.post('https://www.linkedin.com/oauth/v2/accessToken', data=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            print('919: NEW ACCESS TOKEN: ', access_token)
            tokens_file = f"{parent_dir}/files/tokens/linkedin_access_token.txt"
            with open(tokens_file, 'w') as file:
                file.write(access_token)
            return access_token
        else:
            return None

    def check_if_access_token_works(access_token):
        MAX_RETRIES = 3
        RETRY_DELAY = 5  # seconds

        print('927')
        print('Access token: ', access_token)
        headers = {'Authorization': f'Bearer {access_token}'}

        for attempt in range(MAX_RETRIES):
            response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
            print('Status code: ', response.status_code)
            print('Response content: ', response.content)

            if response.status_code == 200:
                linkedin_id = response.json().get('id')
                return True, linkedin_id
            else:
                print("Attempt {} failed. Invalid or expired token.".format(attempt + 1))

                # If this wasn't the last attempt, then wait before retrying
                if attempt < MAX_RETRIES - 1:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

        print("All attempts failed. Please generate a new token.")
        return False, None

    tokens_file = f"{parent_dir}/files/tokens/linkedin_access_token.txt"
    print('934: ', tokens_file)
    linkedin_id = None
    access_token = None
    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as file:
            access_token = file.read().rstrip('\n')
            does_it_work, linkedin_id = check_if_access_token_works(access_token)
            if does_it_work == False:
                access_token = None

    if access_token is None:
        access_code = generate_new_access_code()
        if access_code is not None:
            access_token = generate_new_access_token(access_code)
            if access_token is not None:
                does_it_work, linkedin_id = check_if_access_token_works(access_token)
                if does_it_work == False:
                    print("Newly generated access token is invalid or expired.")
                    return

    if access_token is None:
        print("Failed to generate access_token.")
        return None, None

    return access_token, linkedin_id


def get_asset_urn_after_uploading_image_to_linkedin(media_url):

    access_token, linkedin_id = get_active_access_token_and_linkedin_id()

    # Step 1: Register the Image

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'x-li-format': 'json'
    }
    url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
    data = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{linkedin_id}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        upload_url = response_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset_urn = response_data['value']['asset']
        print('Image registered successfully.')
        print(f'Upload URL: {upload_url}')
    else:
        print('Failed to register the image.')
        print(f'Status code: {response.status_code}')
        print(f'Response: {response_data}')

    # Step 2: Upload Image Binary File

    image_response = requests.get(media_url)

    if image_response.status_code == 200:
        image_binary = io.BytesIO(image_response.content).read()
    else:
        print('Failed to download the image from Google Cloud Storage.')
        print(f'Status code: {image_response.status_code}')
        print(f'Response: {image_response.text}')
        exit()

    upload_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    upload_response = requests.post(upload_url, headers=upload_headers, data=image_binary)

    # Check if the upload was successful
    if upload_response.status_code == 201:
        print('Image uploaded successfully.')
        print(asset_urn)
        return(asset_urn)
    else:
        print('Failed to upload the image.')
        print(f'Status code: {upload_response.status_code}')
        print(f'Response: {upload_response.text}')

def fn_unpublish_note(note_id):

    cursor = conn.cursor()
    default_date = datetime.datetime.now(tz).strftime('%Y-%m-%d')
    date = called_function_arguments_dict.get('date', default_date)

    def delete_tweets_by_note_id(note_id):
        select_cmd = "SELECT id, tweet_id FROM tweets WHERE note_id = %s"
        cursor.execute(select_cmd, (note_id,))
        results = cursor.fetchall()
        if not results:
            print(colored(f"No published tweets to delete for note id {note_id}", 'cyan'))
        else:
            oauth = get_oauth_session()
            for result in results:
                table_id, tweet_id = result
                time.sleep(1)
                # Delete the tweet on Twitter
                url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                response = oauth.delete(url)
                # Check for a successful response
                if response.status_code == 200:
                # If the deletion was successful on Twitter, delete the record from the tweets table
                    sql = "DELETE FROM tweets WHERE id = %s"
                    cursor.execute(sql, (table_id,))
                else:
                    print(colored(f"Failed to delete tweet with {tweet_id} for note id {note_id}", 'cyan'))
                    print(response.text)

    def delete_linkedin_post_by_note_id(note_id):
        select_cmd = "SELECT id, note_id, post_id FROM linkedin_posts WHERE note_id = %s"
        cursor.execute(select_cmd, (note_id,))
        result = cursor.fetchone()
        if not result:
            print(colored(f"No published linkedin posts to delete for note id {note_id}", 'cyan'))
        else:
            table_id, note_id, post_id = result
            access_token, linkedin_id = get_active_access_token_and_linkedin_id()
            time.sleep(1)

            # Note that URNs included in the URL params must be URL encoded. For example, urn:li:ugcPost:12345 would become urn%3Ali%3AugcPost%3A12345.
            encoded_post_id = urllib.parse.quote(post_id, safe='')
            url = f"https://api.linkedin.com/v2/ugcPosts/{encoded_post_id}"
            print(url)


            headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            response = requests.delete(url, headers=headers)

            if response.status_code == 200 or response.status_code == 204:
                # If the deletion was successful, delete the record from the tweets table
                sql = "DELETE FROM linkedin_posts WHERE id = %s"
                cursor.execute(sql, (table_id,))

            print('852', response, response.status_code, response.content)
            if response.status_code != 201 and response.status_code != 204:
                print('726')
                print(colored(f"Request returned an error with status code {response.status_code}", "cyan"))
                print(colored(response.text, "cyan"))
                return False
            else:
                print(f"Deleted note id {note_id} from LinkedIn")


    def set_is_published_to_false(note_id):
        print(colored(f"Setting note id {note_id} as unpublished", "cyan"))
        update_cmd = "UPDATE notes SET is_published = 0, published_at = NULL WHERE id = %s"
        cursor.execute(update_cmd, (note_id,))
        conn.commit()
        return True

    try:
        delete_tweets_by_note_id(note_id)
        delete_linkedin_post_by_note_id(note_id)
        set_is_published_to_false(note_id)
    except Exception as e:
        print('line 809 error', e)


if __name__ == '__main__':
    publish_or_improvise_notes()


