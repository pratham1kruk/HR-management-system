from flask import Blueprint, render_template
from models.mongo_models import get_personnel_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")

@mongo_analytics_bp.route("/")
def mongo_stats():
    collection = get_personnel_collection()

    # 1. Missing PAN details
    missing_pan = collection.find({"pan": {"$exists": False}})
    missing_pan_data = [(doc.get("name", "N/A"), str(doc["_id"])) for doc in missing_pan]

    # 2. Qualification count
    qualification_pipeline = [
        {"$group": {"_id": "$qualification", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    qualification_data = list(collection.aggregate(qualification_pipeline))

    # 3. City-wise Count
    city_pipeline = [
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    city_data = list(collection.aggregate(city_pipeline))

    # 4. State-wise Count
    state_pipeline = [
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_data = list(collection.aggregate(state_pipeline))

    # 5. Gender Stats
    total_employees = collection.count_documents({})
    gender_male = collection.count_documents({"gender": "Male"})
    gender_female = collection.count_documents({"gender": "Female"})
    gender_stats = {
        "male": gender_male,
        "female": gender_female,
        "male_percent": round((gender_male / total_employees) * 100, 2) if total_employees else 0,
        "female_percent": round((gender_female / total_employees) * 100, 2) if total_employees else 0
    }

    # 6. Blood Group Count with Toggleable Employee IDs
    blood_pipeline = [
        {"$group": {
            "_id": "$blood_group",
            "count": {"$sum": 1},
            "employee_ids": {"$push": "$employee_id"}
        }},
        {"$sort": {"count": -1}}
    ]
    blood_data = list(collection.aggregate(blood_pipeline))

    return render_template("mongo_stats.html",
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data,
        city_data=city_data,
        state_data=state_data,
        gender_stats=gender_stats,
        blood_data=blood_data
    )
