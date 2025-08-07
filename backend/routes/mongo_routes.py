from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from bson.objectid import ObjectId
from app import mongo

mongo_bp = Blueprint('mongo', __name__, url_prefix='/personnel')


# ─────────────────────────────
# 0. Home
# ─────────────────────────────
@mongo_bp.route('/home')
def personnel_home():
    return render_template('personnel_home.html')


# ─────────────────────────────
# 1. List All Personnel
# ─────────────────────────────
@mongo_bp.route('/')
def list_personnel():
    personnel = list(mongo.db.employees_info.find())
    return render_template('personnel_info.html', personnel=personnel)


# ─────────────────────────────
# 2. Add Personnel
# ─────────────────────────────
@mongo_bp.route('/add', methods=['GET', 'POST'])
def add_personnel():
    if request.method == 'POST':
        gender = request.form.get("gender", "").strip().capitalize()
        data = {
            "employee_id": request.form.get("employee_id"),
            "name": request.form.get("name"),
            "aadhaar": request.form.get("aadhaar"),
            "pan": request.form.get("pan"),
            "dob": request.form.get("dob"),
            "gender": gender,
            "blood_group": request.form.get("blood_group"),
            "residence": {
                "address": request.form.get("address"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip")
            },
            "contact": {
                "phone": request.form.get("phone"),
                "email": request.form.get("email")
            },
            "emergency_contact": {
                "name": request.form.get("emergency_name"),
                "phone": request.form.get("emergency_phone")
            },
            "family": {
                "marital_status": request.form.get("marital_status"),
                "no_of_dependents": int(request.form.get("no_of_dependents") or 0),
                "dependents": []
            }
        }

        for i in range(1, 6):
            dep_name = request.form.get(f"dep_name_{i}")
            dep_relation = request.form.get(f"dep_relation_{i}")
            dep_age = request.form.get(f"dep_age_{i}")
            if dep_name and dep_relation and dep_age:
                data["family"]["dependents"].append({
                    "name": dep_name,
                    "relation": dep_relation,
                    "age": int(dep_age)
                })

        mongo.db.employees_info.insert_one(data)
        return redirect(url_for('mongo.list_personnel'))

    return render_template('personnel_form.html', action="Add", data={})


# ─────────────────────────────
# 3. Update Personnel
# ─────────────────────────────
@mongo_bp.route('/update/<id>', methods=['GET', 'POST'])
def update_personnel(id):
    try:
        obj_id = ObjectId(id)
    except Exception:
        return "Invalid ID format", 400

    existing = mongo.db.employees_info.find_one({"_id": obj_id})
    if not existing:
        return "Record not found", 404

    if request.method == 'POST':
        gender = request.form.get("gender", "").strip().capitalize()
        updated = {
            "employee_id": request.form.get("employee_id"),
            "name": request.form.get("name"),
            "aadhaar": request.form.get("aadhaar"),
            "pan": request.form.get("pan"),
            "dob": request.form.get("dob"),
            "gender": gender,
            "blood_group": request.form.get("blood_group"),
            "residence": {
                "address": request.form.get("address"),
                "city": request.form.get("city"),
                "state": request.form.get("state"),
                "zip": request.form.get("zip")
            },
            "contact": {
                "phone": request.form.get("phone"),
                "email": request.form.get("email")
            },
            "emergency_contact": {
                "name": request.form.get("emergency_name"),
                "phone": request.form.get("emergency_phone")
            },
            "family": {
                "marital_status": request.form.get("marital_status"),
                "no_of_dependents": int(request.form.get("no_of_dependents") or 0),
                "dependents": []
            }
        }

        for i in range(1, 6):
            dep_name = request.form.get(f"dep_name_{i}")
            dep_relation = request.form.get(f"dep_relation_{i}")
            dep_age = request.form.get(f"dep_age_{i}")
            if dep_name and dep_relation and dep_age:
                updated["family"]["dependents"].append({
                    "name": dep_name,
                    "relation": dep_relation,
                    "age": int(dep_age)
                })

        mongo.db.employees_info.update_one({"_id": obj_id}, {"$set": updated})
        return redirect(url_for('mongo.list_personnel'))

    return render_template('personnel_form.html', action="Update", data=existing)


# ─────────────────────────────
# 4. Delete Personnel
# ─────────────────────────────
@mongo_bp.route('/delete/<id>', methods=['GET'])
def delete_personnel(id):
    try:
        mongo.db.employees_info.delete_one({"_id": ObjectId(id)})
    except Exception:
        return "Invalid ID", 400
    return redirect(url_for('mongo.list_personnel'))


# ─────────────────────────────
# 5. View Single Personnel (JSON)
# ─────────────────────────────
@mongo_bp.route('/<id>', methods=['GET'])
def view_personnel(id):
    try:
        person = mongo.db.employees_info.find_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not person:
        return jsonify({"error": "Not found"}), 404

    person["_id"] = str(person["_id"])
    return jsonify(person)


# ─────────────────────────────
# 6. Blood Group Stats View
# ─────────────────────────────
@mongo_bp.route('/analytics/bloodgroup-count')
def bloodgroup_counts():
    pipeline = [
        {"$group": {"_id": "$blood_group", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(mongo.db.employees_info.aggregate(pipeline))
    return render_template(
        "stats.html",
        title="Count by Blood Group",
        data=[(r["_id"], r["count"]) for r in results],
        label1="Blood Group", label2="Count"
    )


# ─────────────────────────────
# 7. Add Qualification & Experience
# ─────────────────────────────
@mongo_bp.route('/add-qualification', methods=['GET', 'POST'])
def add_qualification():
    if request.method == 'POST':
        emp_id = request.form.get("employee_id")
        name = request.form.get("name")
        qualifications = request.form.getlist("qualification[]")
        experiences = request.form.getlist("experience[]")

        if not emp_id:
            return "Employee ID is required", 400

        # Clean out empty entries
        qualifications = [q for q in qualifications if q.strip()]
        experiences = [e for e in experiences if e.strip()]

        data = {
            "employee_id": emp_id.strip(),
            "name": name.strip() if name else "",
            "qualifications": qualifications,
            "experiences": experiences
        }

        mongo.db.qualifications.insert_one(data)
        return redirect(url_for('mongo.list_personnel'))

    return render_template("qualification.html")
