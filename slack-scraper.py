import os
from dotenv import load_dotenv
from slack_sdk import WebClient
import chromadb

load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

chroma_client = chromadb.HttpClient()
collection_search = client.get_or_create_collection(name="search")

def scrape_channel(channel_id):
    response = client.conversations_history(channel=channel_id)
    messages = response["messages"]
    while response['has_more']:
        response = client.conversations_history(channel=channel_id, cursor=response['response_metadata']['next_cursor'])
        messages += response["messages"]
    
    documents = []
    metadata = []
    ids = []
    for message in messages:
        documents.append(message['text'])
        metadata.append({'ts': message['ts'], 'channel': channel_id})
        ids.append(message['ts'])
    collection_search.upsert(documents=documents, metadata=metadata, ids=ids)
