__import__('pysqlite3')
import sys

import chromadb.server
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import os
import chromadb
import subprocess
subprocess.run(["chroma", "run", "--path", "/db"])