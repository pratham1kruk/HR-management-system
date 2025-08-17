# models/mongo_models.py
from flask import current_app

def get_mongo():
    return current_app.config['MONGO']

def get_personnel_collection():
    """Get the main personnel collection (employees_info)."""
    mongo = get_mongo()
    return mongo.db.employees_info

def get_qualification_collection():
    """
    Get the 'qualifications' collection if it exists, else return None.
    Caller should fall back to personnel collection if not present.
    """
    mongo = get_mongo()
    db = mongo.db
    # list_collection_names() is cheap enough here
    if 'qualifications' in db.list_collection_names():
        return db.qualifications
    return None
