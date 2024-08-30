# replacing the system sqlite3 version with pysqlite3 (because chromadb doesn't work with the system version shipped in Github Codespaces)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv
from slack_sdk import WebClient
import chromadb

# get secrets
load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

# initialize Slack Web client
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# define the channels to scrape
search_channels = ['C07G0TYHAGP']

# initialize Chroma db client
#chroma_client = chromadb.HttpClient()
chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

# Message subtypes that should be excluded from the database
excluded_subtypes = ['channel_join', 'channel_topic']

# function to scrape a channel
def scrape_channel(channel_id):
    # get messages from channel with pagination
    response = client.conversations_history(channel=channel_id)
    messages = response["messages"]
    while response['has_more']:
        response = client.conversations_history(channel=channel_id, cursor=response['response_metadata']['next_cursor'])
        messages += response["messages"]
    
    documents = []
    metadata = []
    ids = []
    added_threads = []
    for message in messages:
        # skip message if subtype in excluded subtypes or already added
        new_id = str(channel_id) + str(message['ts'])
        if message.get('subtype') in excluded_subtypes or new_id in ids:
            continue
        print(message)
        # add message data to list
        documents.append(message['text'])
        metadata.append({'type': 'slack','ts': message['ts'], 'channel': channel_id})
        ids.append(new_id)
        # get replies if message has a thread (with pagination)
        if message.get('reply_count') and message.get('thread_ts') not in added_threads:
            response = client.conversations_replies(channel=channel_id, ts=message['thread_ts'])
            messages += response['messages']
            while response['has_more']:
                response = client.conversations_replies(channel=channel_id, ts=message['thread_ts'], cursor=response['response_metadata']['next_cursor'])
                messages += response["messages"]
            added_threads.append(message['thread_ts'])

    # embed messages in vector db
    collection_search.upsert(documents=documents, metadatas=metadata, ids=ids)

# scrape all channels in search_channels
for channel in search_channels:
    scrape_channel(channel)
