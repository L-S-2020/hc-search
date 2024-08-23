# replacing the system sqlite3 version with pysqlite3 (because chromadb doesn't work with the system version shipped in Github Codespaces)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from github import Auth
from github import Github
from github import GithubIntegration
import chromadb

import markdown
import semchunk
from bs4 import BeautifulSoup

import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
CHUNK_SIZE = 1000

chunker = semchunk.chunkerify(lambda text: len(text), CHUNK_SIZE)

# initialize Chroma db client
#chroma_client = chromadb.HttpClient()
chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)

exclude_characters = ['\\\n', '\\n', '\n', "b'#", '#',]



def scrape_repo(Reponsitory):
    documents = []
    metadata = []
    ids = []
    title = Reponsitory.full_name
    description = Reponsitory.description
    content = repo.get_contents("")
    while content:
        file = content.pop(0)
        if file.type == "dir":
            content.extend(repo.get_contents(file.path))
        else:
            if file.path.endswith('.md'):
                md_text = file.decoded_content
                html_text = markdown.markdown(md_text)
                soup = BeautifulSoup(html_text, 'html.parser')
                chunks = chunker(soup.get_text())
                for chunk in chunks:
                    item = chunks.index(chunk)
                    for character in exclude_characters:
                        chunk = chunk.replace(character, ' ')
                    documents.append(chunk)
                    metadata.append({'type': 'github','repo': title, 'file': file.path, 'url': file.html_url})
                    ids.append(title + file.path + str(item))
    collection_search.upsert(documents=documents, metadatas=metadata, ids=ids)
    print('scraped: ' + title)



org = g.get_organization("hackclub")

for repo in org.get_repos():
    print(repo)
    scrape_repo(repo)