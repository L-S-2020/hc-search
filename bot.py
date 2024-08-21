__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
import chromadb

load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_SOCKET_TOKEN = os.environ['SLACK_SOCKET_TOKEN']

client = SocketModeClient(
    app_token=SLACK_SOCKET_TOKEN,
    web_client=WebClient(token=SLACK_BOT_TOKEN)
)

#chroma_client = chromadb.HttpClient()
#collection_search = client.get_or_create_collection(name="search")

def listener(client: SocketModeClient, req: SocketModeRequest):
    print(req)

client.socket_mode_request_listeners.append(listener)
client.connect()

from threading import Event
Event().wait()