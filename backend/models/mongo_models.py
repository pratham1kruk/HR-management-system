# backend/models/mongo_models.py

from flask import current_app

def get_mongo():
    return current_app.config['MONGO']

def get_personnel_collection():
    mongo = get_mongo()
    return mongo.db.employees_info  # ✅ This is correct and safe

