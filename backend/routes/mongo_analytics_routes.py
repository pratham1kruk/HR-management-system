from flask import Blueprint, render_template, jsonify
from models.mongo_models import get_personnel_collection, get_qualification_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")

@mongo_analytics_bp.route("/")
def mongo_stats():
    personnel_col = get_personnel_collection()
    qualification_col = get_qualification_collection()

    # 1. Missing PAN
    missing_pan = personnel_col.find({"pan": {"$exists": False}})
    missing_pan_data = [(doc.get("name", "N/A"), doc.get("employee_id", "N/A")) for doc in missing_pan]

    # 2. Qualifications per employee
    qualification_pipeline = [
        {"$group": {
            "_id": "$employee_id",
            "name": {"$first": "$name"},
            "qualifications": {"$push": "$qualification"}
        }},
        {"$project": {
            "_id": 1,
            "name": 1,
            "qualifications": 1,
            "count": {"$size": "$qualifications"}
        }},
        {"$sort": {"count": -1}}
    ]
    qualification_data = list(qualification_col.aggregate(qualification_pipeline))

    # 3. City-wise Count
    city_pipeline = [
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    city_data = list(personnel_col.aggregate(city_pipeline))

    # 4. State-wise Count
    state_pipeline = [
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_data = list(personnel_col.aggregate(state_pipeline))

    # 5. Gender distribution
    total_personnel = personnel_col.count_documents({})
    gender_pipeline = [
        {"$group": {"_id": "$gender", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    gender_data = list(personnel_col.aggregate(gender_pipeline))

    return render_template(
        "mongo_stats.html",
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data,
        city_data=city_data,
        state_data=state_data,
        gender_data=gender_data,
        total_personnel=total_personnel
    )


# New API endpoint for Search Bar to get past experience
@mongo_analytics_bp.route("/experience/<emp_id>")
def get_experience(emp_id):
    qualification_col = get_qualification_collection()
    records = qualification_col.find({"employee_id": emp_id}, {"experience": 1, "_id": 0})
    
    # Flatten experiences, remove None/empty
    experiences = []
    for rec in records:
        exp_list = rec.get("experience")
        if isinstance(exp_list, list):
            experiences.extend([e for e in exp_list if e])
        elif isinstance(exp_list, str) and exp_list.strip():
            experiences.append(exp_list.strip())

    return jsonify({"experience": experiences})
