from flask import Blueprint, render_template
from db.mongo_connection import get_personnel_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")

@mongo_analytics_bp.route("/")
def mongo_stats():
    collection = get_personnel_collection()

    # 1. Missing PAN details
    missing_pan = collection.find({"pan": {"$exists": False}})
    missing_pan_data = [(doc.get("name", "N/A"), str(doc["_id"])) for doc in missing_pan]

    # 2. Qualification count
    pipeline = [
        {"$group": {"_id": "$qualification", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    qualification_counts = collection.aggregate(pipeline)
    qualification_data = [(doc["_id"], doc["count"]) for doc in qualification_counts]

    return render_template("mongo_stats.html",
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data
    )
