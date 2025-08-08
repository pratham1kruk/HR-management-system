from flask import Blueprint, render_template, request
from models.mongo_models import get_personnel_collection, get_qualification_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")

@mongo_analytics_bp.route("/", methods=["GET"])
def mongo_stats():
    personnel_coll = get_personnel_collection()
    qual_coll = get_qualification_collection()

    qualification_data = []
    if qual_coll is not None:
        qualification_pipeline = [
            {
                "$group": {
                    "_id": "$employee_id",
                    "name": {"$first": "$name"},
                    "qualifications": {"$first": "$qualifications"},
                    "experiences": {"$first": "$experiences"},
                    "count": {"$sum": {"$size": "$qualifications"}}
                }
            },
            {"$sort": {"count": -1}}
        ]
        qualification_data = list(qual_coll.aggregate(qualification_pipeline))

    city_data = list(personnel_coll.aggregate([
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    state_data = list(personnel_coll.aggregate([
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))

    total_employees = personnel_coll.count_documents({})
    gender_male = personnel_coll.count_documents({"gender": "Male"})
    gender_female = personnel_coll.count_documents({"gender": "Female"})
    gender_stats = {
        "male": gender_male,
        "female": gender_female,
        "male_percent": round((gender_male / total_employees) * 100, 2) if total_employees else 0,
        "female_percent": round((gender_female / total_employees) * 100, 2) if total_employees else 0
    }

    blood_data = list(personnel_coll.aggregate([
        {
            "$group": {
                "_id": "$blood_group",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]))

    return render_template(
        "mongo_stats.html",
        qualification_data=qualification_data,
        city_data=city_data,
        state_data=state_data,
        gender_stats=gender_stats,
        blood_data=blood_data,
        total_personnel=total_employees
    )
