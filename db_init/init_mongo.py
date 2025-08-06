from pymongo import MongoClient
import json

client = MongoClient("mongodb://root:example@127.0.0.1:27017/?authSource=admin")
db = client["hrmongo"]

with open("db_init/personnel_info.json") as f:
    data = json.load(f)

# Insert into a collection named "employees_info"
db.employees_info.insert_many(data)
print("Inserted personnel_info.json into employees_info collection")
