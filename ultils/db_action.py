import motor.motor_asyncio
from dotenv import load_dotenv
from os import getenv
import pprint

load_dotenv()

class Database:
    def __init__(self, collection_name):
        self.CONNECTION_STRING = getenv("MONGODB_URI")
        # cluster = MongoClient(CONNECTION_STRING)
        # self.db = cluster["discordDB"]
        self.collection = collection_name
        self.db = None
    
    async def connect(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(self.CONNECTION_STRING)
        cluster = client['discordDB']
        self.db = cluster[self.collection]
        
    async def insert(self, key):
        await self.db.insert_one(key)
        
    async def find(self, key):
        find = self.db.find(key)
        if not find:
            return None
        
        async for i in find:
            return pprint.pformat(i)
        
    async def remove(self, key):
        await self.db.delete_one(key)
        
async def getDB(name):
    db = Database(name)
    await db.connect()
    return db


        
