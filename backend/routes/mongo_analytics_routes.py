from flask import Blueprint, render_template, request
from models.mongo_models import get_personnel_collection, get_qualification_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")


@mongo_analytics_bp.route("/", methods=["GET"])
def mongo_stats():
    # Get collections
    personnel_coll = get_personnel_collection()
    qual_coll = get_qualification_collection()

    # 1. Missing PAN details
    missing_pan = personnel_coll.find({"pan": {"$exists": False}})
    missing_pan_data = [(doc.get("name", "N/A"), str(doc["_id"])) for doc in missing_pan]

    # 2. Qualification counts per employee (from qualification collection)
    qualification_data = []
    if qual_coll is not None:
        qualification_pipeline = [
            {
                "$group": {
                    "_id": "$employee_id",
                    "name": {"$first": "$name"},
                    "qualifications": {"$push": "$qualification"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        qualification_data = list(qual_coll.aggregate(qualification_pipeline))

    # 3. City-wise Count
    city_pipeline = [
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    city_data = list(personnel_coll.aggregate(city_pipeline))

    # 4. State-wise Count
    state_pipeline = [
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_data = list(personnel_coll.aggregate(state_pipeline))

    # 5. Gender Stats
    total_employees = personnel_coll.count_documents({})
    gender_male = personnel_coll.count_documents({"gender": "Male"})
    gender_female = personnel_coll.count_documents({"gender": "Female"})
    gender_stats = {
        "male": gender_male,
        "female": gender_female,
        "male_percent": round((gender_male / total_employees) * 100, 2) if total_employees else 0,
        "female_percent": round((gender_female / total_employees) * 100, 2) if total_employees else 0
    }

    # 6. Blood Group Count with Toggleable Employee IDs
    blood_pipeline = [
        {
            "$group": {
                "_id": "$blood_group",
                "count": {"$sum": 1},
                "employee_ids": {"$push": "$employee_id"}
            }
        },
        {"$sort": {"count": -1}}
    ]
    blood_data = list(personnel_coll.aggregate(blood_pipeline))

    # 7. Search bar for employee qualifications
    search_results = []
    emp_id = request.args.get("emp_id")
    if emp_id:
        if qual_coll is not None:
            search_results = list(qual_coll.find({"employee_id": emp_id}))
        else:
            search_results = []

    return render_template(
        "mongo_stats.html",
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data,
        city_data=city_data,
        state_data=state_data,
        gender_stats=gender_stats,
        blood_data=blood_data,
        search_results=search_results
    )
