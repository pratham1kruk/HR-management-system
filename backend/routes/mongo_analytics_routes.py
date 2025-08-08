# routes/mongo_analytics_routes.py
from flask import Blueprint, render_template, request
from models.mongo_models import get_personnel_collection, get_qualification_collection

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/mongo-analytics")

@mongo_analytics_bp.route("/")
def mongo_stats():
    personnel = get_personnel_collection()
    qual_coll = get_qualification_collection()

    # 1) Missing PAN: check exist / null / empty
    missing_pan_cursor = personnel.find({
        "$or": [
            {"pan": {"$exists": False}},
            {"pan": None},
            {"pan": ""}
        ]
    })
    missing_pan_data = [(doc.get("name", "N/A"), str(doc["_id"])) for doc in missing_pan_cursor]

    # 2) Qualification counts:
    if qual_coll:
        # dedicated qualifications collection: assume documents have { employee_id, qualification } or similar
        qualification_pipeline = [
            {"$unwind": {"path": "$qualification", "preserveNullAndEmptyArrays": False}},
            {"$group": {"_id": "$qualification", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        qualification_data = list(qual_coll.aggregate(qualification_pipeline))
    else:
        # fallback: derive from personnel collection (works when personnel docs contain an array field named 'qualification' or 'qualifications')
        qualification_pipeline = [
            {"$project": {"quals": {"$ifNull": ["$qualification", "$qualifications"]}}},
            {"$unwind": {"path": "$quals", "preserveNullAndEmptyArrays": False}},
            {"$group": {"_id": "$quals", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        qualification_data = list(personnel.aggregate(qualification_pipeline))

    # 3) City-wise and state-wise counts
    city_pipeline = [
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    city_data = list(personnel.aggregate(city_pipeline))

    state_pipeline = [
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_data = list(personnel.aggregate(state_pipeline))

    # 4) Gender stats
    total_employees = personnel.count_documents({})
    gender_male = personnel.count_documents({"gender": "Male"})
    gender_female = personnel.count_documents({"gender": "Female"})
    gender_stats = {
        "male": gender_male,
        "female": gender_female,
        "male_percent": round((gender_male / total_employees) * 100, 2) if total_employees else 0,
        "female_percent": round((gender_female / total_employees) * 100, 2) if total_employees else 0
    }

    # 5) Blood group data with list of employee_ids (toggle-able in template)
    blood_pipeline = [
        {"$group": {
            "_id": "$blood_group",
            "count": {"$sum": 1},
            "employee_ids": {"$push": "$employee_id"}
        }},
        {"$sort": {"count": -1}}
    ]
    blood_data = list(personnel.aggregate(blood_pipeline))

    # 6) Emp search: if ?emp_id=E001 provided show qualifications and experiences for that employee
    emp_id = request.args.get("emp_id", "").strip()
    emp_details = None
    if emp_id:
        if qual_coll:
            # qualifications stored in separate collection
            # try to fetch all qualification documents for this emp_id
            qdocs = list(qual_coll.find({"employee_id": emp_id}, {"_id": 0}))
            if qdocs:
                # normalization: gather qualifications and experiences
                qual_list = []
                exp_list = []
                for d in qdocs:
                    if isinstance(d.get("qualification"), list):
                        qual_list.extend(d.get("qualification"))
                    elif d.get("qualification"):
                        qual_list.append(d.get("qualification"))
                    if isinstance(d.get("experience"), list):
                        exp_list.extend(d.get("experience"))
                    elif d.get("experience"):
                        exp_list.append(d.get("experience"))
                emp_details = {
                    "employee_id": emp_id,
                    "name": qdocs[0].get("name") or "",
                    "qualifications": qual_list,
                    "experiences": exp_list
                }
            else:
                # fallback: try personnel collection
                p = personnel.find_one({"employee_id": emp_id})
                if p:
                    emp_details = {
                        "employee_id": emp_id,
                        "name": p.get("name"),
                        "qualifications": p.get("qualification") or p.get("qualifications") or [],
                        "experiences": p.get("experience") or []
                    }
        else:
            p = personnel.find_one({"employee_id": emp_id})
            if p:
                emp_details = {
                    "employee_id": emp_id,
                    "name": p.get("name"),
                    "qualifications": p.get("qualification") or p.get("qualifications") or [],
                    "experiences": p.get("experience") or []
                }

    return render_template(
        "mongo_stats.html",
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data,
        city_data=city_data,
        state_data=state_data,
        gender_stats=gender_stats,
        blood_data=blood_data,
        emp_details=emp_details,
        query_emp_id=emp_id
    )
