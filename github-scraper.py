# replacing the system sqlite3 version with pysqlite3 (because chromadb doesn't work with the system version shipped in Github Codespaces)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# importing the necessary libraries
from github import Auth
from github import Github
from github import GithubIntegration
import chromadb

import markdown
import semchunk
from bs4 import BeautifulSoup

# getting secrets
import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
CHUNK_SIZE = 1000

# set up chunker function
chunker = semchunk.chunkerify(lambda text: len(text), CHUNK_SIZE)

# initialize Chroma db client
#chroma_client = chromadb.HttpClient()
chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

# login to Github
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)

# define the characters to exclude
exclude_characters = ['\\\n', '\\n', '\n', "b'#", '#',]


# define scraping function
def scrape_repo(Reponsitory):
    documents = []
    metadata = []
    ids = []
    # get the repo title, description, and contents
    title = Reponsitory.full_name
    description = Reponsitory.description
    content = repo.get_contents("")
    # iterate through the contents
    while content:
        file = content.pop(0)
        # if content is a directory, add the contents of the directory
        if file.type == "dir":
            content.extend(repo.get_contents(file.path))
        else:
            # if content is a markdown file, get the text
            if file.path.endswith('.md'):
                md_text = file.decoded_content
                # convert the markdown text to html
                html_text = markdown.markdown(md_text)
                # scrape the html text
                soup = BeautifulSoup(html_text, 'html.parser')
                # chunk the text
                chunks = chunker(soup.get_text())
                # format for chroma db
                for chunk in chunks:
                    item = chunks.index(chunk)
                    for character in exclude_characters:
                        chunk = chunk.replace(character, ' ')
                    documents.append(chunk)
                    metadata.append({'type': 'github','title': title, 'file': file.path, 'url': file.html_url})
                    ids.append(title + file.path + str(item))
    # add to chroma db
    collection_search.upsert(documents=documents, metadatas=metadata, ids=ids)
    print('scraped: ' + title)


# get the hackclub organization
org = g.get_organization("hackclub")

# scrape every repo in the organization
for repo in org.get_repos():
    print(repo)
    scrape_repo(repo)