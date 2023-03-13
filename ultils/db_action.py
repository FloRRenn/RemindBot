import motor.motor_asyncio
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
    
    # async def connect(self):
    #     client = motor.motor_asyncio.AsyncIOMotorClient(self.CONNECTION_STRING)
    #     cluster = client['discordDB']
    #     self.db = cluster[self.collection]
        
    def insert(self, key):
        self.collection.insert_one(key)
        
    def get_all(self):
        return self.collection.find({})
        
    def find(self, key):
        find = self.collection.find(key)
        if not find:
            return None
        
        for i in find:
            return pprint.pformat(i)
        
    def remove(self, key):
        self.collection.delete_one(key)
        
    def update(self, key):
        self.collection.update_one(key)


        
