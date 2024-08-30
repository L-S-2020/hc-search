# replacing the system sqlite3 version with pysqlite3 (because chromadb doesn't work with the system version shipped in Github Codespaces)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# importing the necessary libraries
import chromadb
import semchunk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# initialize Chroma db client
chroma_client = chromadb.HttpClient()
#chroma_client = chromadb.PersistentClient(path="db")
collection_search = chroma_client.get_or_create_collection(name="search")

# initialize/install the web driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.implicitly_wait(5)

# define the chunk size and the characters to exclude
CHUNK_SIZE = 1000
exclude_characters = ['\\\n', '\\n', '\n', "b'#", '#',]
chunker = semchunk.chunkerify(lambda text: len(text), CHUNK_SIZE)

# define the waitlist and the scraped list
waitlist = ['https://hackclub.com']
scraped = []
connect = {}

# repeat until the waitlist is empty
while waitlist != []:
    # get url from the waitlist
    current = waitlist.pop(0)
    if current not in scraped:
        try:
            # scrape the website and get the text
            driver.get(current)
            text = driver.find_element(By.XPATH, "/html/body").text
        except:
            continue
        try:
            # get all the links from the website
            for link in driver.find_elements(By.XPATH, "//a[@href]"):
                l = link.get_attribute('href')
                if '#' in l:
                    l = l[:l.index('#')]
                # if 'hackclub' is in the link and it is not in the scraped list or the waitlist, add it to the waitlist
                if l not in scraped and 'hackclub' in l and l not in waitlist:
                    waitlist.append(l)
        except Exception as e:
            print(e)
        try:
            # get the title of the website
            title = driver.title
            print(title)
        except:
            title = str(current)
        content = []
        metadata = []
        ids = []
        # chunk the text
        chunks = chunker(text)
        for chunk in chunks:
            item = chunks.index(chunk)
            for character in exclude_characters:
                chunk = chunk.replace(character, ' ')
            content.append(chunk)
            metadata.append({"type": 'website', "url": current, "title": title})
            ids.append(current + str(item))
        # add the scraped data to the chroma db
        collection_search.add(
            documents=content,
            metadatas=metadata,
            ids=ids,
        )
        # add the current website to scraped list
        scraped.append(current)
        print('Scraped ' + str(current))
# close the web driver / browser
driver.quit()