# replacing sqlite for chroma/codespaces
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# set up logging
import logging
logging.basicConfig(format='{asctime} - {levelname} - {message}', style='{', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# importing packages
import os
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
import chromadb

# getting secrets
load_dotenv()
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_SOCKET_TOKEN = os.environ['SLACK_SOCKET_TOKEN']

# initialize Slack client
client = SocketModeClient(
    app_token=SLACK_SOCKET_TOKEN,
    web_client=WebClient(token=SLACK_BOT_TOKEN)
)

# initialize Chroma db client
chroma_client = chromadb.HttpClient()
#chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

# define listener function
def listener(client: SocketModeClient, req: SocketModeRequest):

	# when slash command recieved
    if req.type == 'slash_commands':
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
        
        # respond to /hc-search
        if req.payload['command'] == '/hc-search':
            # log the request
            logging.info(f"Search request from {req.payload['user_id']} in {req.payload['channel_id']} for {req.payload['text']}")
            # search in chroma db
            results = collection_search.query(query_texts=[req.payload['text'],], n_results=3)
            # add links to slack messages
            for metadata in results['metadatas'][0]:
                if metadata['type'] == 'slack':
                    url = client.web_client.chat_getPermalink(channel=metadata['channel'], message_ts=metadata['ts'])
                    metadata['url'] = url['permalink']
                    metadata['title'] = '<#' + metadata['channel'] +'>'
            # format message
            block =[
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
				"text": "*" + results['metadatas'][0][0]['title'] + "*\n" + results['metadatas'][0][0]['type'] + "\n " + results['documents'][0][0] + "\n " + results['metadatas'][0][0]['url'],
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open"
				},
				"value": "click_me_123",
				"url": results['metadatas'][0][0]['url']
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*" + results['metadatas'][0][1]['title'] + "*\n" + results['metadatas'][0][1]['type'] + "\n " + results['documents'][0][1] + "\n " + results['metadatas'][0][1]['url'],
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open"
				},
				"value": "click_me_123",
				"url": results['metadatas'][0][0]['url']
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*" + results['metadatas'][0][1]['title'] + "*\n" + results['metadatas'][0][1]['type'] + "\n " + results['documents'][0][1] + "\n " + results['metadatas'][0][1]['url'],
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Open"
				},
				"value": "click_me_123",
				"url": results['metadatas'][0][0]['url']
			}
		}
	]
            # send message
            client.web_client.chat_postEphemeral(channel=req.payload['channel_id'], user=req.payload['user_id'], blocks=block, text='Search results')

# add listener to client
client.socket_mode_request_listeners.append(listener)
client.connect()

# wait forever
from threading import Event
Event().wait()