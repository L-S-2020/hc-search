# replacing the system sqlite3 version with pysqlite3 (because chromadb doesn't work with the system version shipped in Github Codespaces)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import semchunk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

#chroma_client = chromadb.HttpClient()
chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.implicitly_wait(5)

exclude_characters = ['\\\n', '\\n', '\n', "b'#", '#',]
chunker = semchunk.chunkerify(lambda text: len(text), CHUNK_SIZE)

waitlist = ['https://hackclub.com']
scraped = []
connect = {}
while waitlist != []:
    current = waitlist.pop(0)
    if current not in scraped:
        try:
            driver.get(current)
            text = driver.find_element(By.XPATH, "/html/body").text
        except:
            continue
        try:
            for link in driver.find_elements(By.XPATH, "//a[@href]"):
                l = link.get_attribute('href')
                if '#' in l:
                    l = l[:l.index('#')]
                if l not in scraped and 'hackclub' in l:
                    waitlist.append(l)
        except Exception as e:
            print(e)
        try:
            title = driver.title
            print(title)
        except:
            title = str(current)
        content = []
        metadata = []
        ids = []
        chunks = chunker(text)
        for chunk in chunks:
            item = chunks.index(chunk)
            for character in exclude_characters:
                chunk = chunk.replace(character, ' ')
            content.append(chunk)
            metadata.append({"type": 'website', "url": current, "name": title})
            ids.append(current + str(item))
        collection_search.add(
            documents=content,
            metadatas=metadata,
            ids=ids,
        )
        scraped.append(current)
        print('Scraped ' + str(current))
driver.quit()