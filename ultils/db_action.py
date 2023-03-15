from dotenv import load_dotenv
from os import getenv
import pprint

from pymongo import MongoClient

load_dotenv()
CONNECTION_STRING = getenv("MONGODB_URI")
cluster = MongoClient(CONNECTION_STRING)
db = cluster["discordDB"]

class Database:
    def __init__(self, collection_name):
        self.collection = db[collection_name]
        
    def insert(self, key):
        self.collection.insert_one(key)
        
    def get_all(self, *args, **kwargs):
        return self.collection.find(*args, **kwargs)
        
    def find(self, *args, **kwargs):
        find = self.collection.find_one(*args, **kwargs)
        if not find:
            return None
        return find
        
    def remove(self, key):
        return self.collection.delete_one(key)
        
    def update(self, *args, **kwargs):
        return self.collection.update_one(*args, **kwargs)
    