import pymongo

myclient = pymongo.MongoClient("mongodb+srv://florren:superMAN@cluster0.6lt2j1x.mongodb.net/test")
mydb = myclient["discordDB"]
mycol = mydb["rooms"]

mydict = { "name": "John", "address": "Highway 37" }

x = mycol.insert_one(mydict)