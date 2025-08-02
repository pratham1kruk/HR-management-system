# db_init/init_mongo.py
import json
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["hr_database"]
collection = db["personnel_info"]

with open("db_init/personnel_info_init.json") as f:
    data = json.load(f)

# Drop existing if needed
collection.drop()
collection.insert_many(data)
print("MongoDB seeded with personnel_info_init.json")
