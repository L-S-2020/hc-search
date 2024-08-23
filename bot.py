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

# initialize Chroma db client
#chroma_client = chromadb.HttpClient()
chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

def listener(client: SocketModeClient, req: SocketModeRequest):
    print(req.type)
    if req.type == 'slash_commands':
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        if req.payload['command'] == '/hc-search':
            results = collection_search.query(query_texts=[req.payload['text'],], n_results=5)
            for metadata in results['metadatas']:
                if metadata['type'] == 'slack':
                    metadata['url'] = client.web_client.chat_getPermalink(metadata['channel'], metadata['ts'])
                    metadata['title'] = '<#' + metadata['channel'] +'>'
            print(req.payload)
            response = {
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Search results for " + req.payload['text']
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Result title*\nLocation\n Result text\n url"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open",
					"emoji": True
				},
				"value": "click_me_123",
				"url": "https://api.slack.com/block-kit"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Result title*\nLocation\n Result text\n url"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open",
					"emoji": True
				},
				"value": "click_me_123",
				"url": "https://api.slack.com/block-kit"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Result title*\nLocation\n Result text\n url"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open",
					"emoji": True
				},
				"value": "click_me_123",
				"url": "https://api.slack.com/block-kit"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "plain_text_input",
				"action_id": "plain_text_input-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Label",
				"emoji": True
			}
		}
	]
}
            client.web_client.chat_postEphemeral(channel=req.payload['channel'], user=req.payload['user'], block=response)


client.socket_mode_request_listeners.append(listener)
client.connect()

from threading import Event
Event().wait()