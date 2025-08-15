from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from bson.objectid import ObjectId
from app import mongo
import pdfkit
import shutil
from flask import make_response
from datetime import datetime

mongo_bp = Blueprint('mongo', __name__, url_prefix='/personnel')

@mongo_bp.route('/home')
def personnel_home():
    return render_template('personnel_home.html')

@mongo_bp.route('/')
def list_personnel():
    personnel = list(mongo.db.employees_info.find())
    return render_template('personnel_info.html', personnel=personnel)

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

@mongo_bp.route('/delete/<id>', methods=['GET'])
def delete_personnel(id):
    try:
        mongo.db.employees_info.delete_one({"_id": ObjectId(id)})
    except Exception:
        return "Invalid ID", 400
    return redirect(url_for('mongo.list_personnel'))

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

@mongo_bp.route('/analytics/bloodgroup/<group>')
def bloodgroup_employees(group):
    results = list(mongo.db.employees_info.find({"blood_group": group}))
    employees = [
        {
            "employee_id": emp.get("employee_id"),
            "name": emp.get("name"),
            "phone": emp.get("contact", {}).get("phone"),
            "email": emp.get("contact", {}).get("email")
        }
        for emp in results
    ]
    return jsonify(employees)

@mongo_bp.route('/add-qualification', methods=['GET', 'POST'])
def add_qualification():
    if request.method == 'POST':
        emp_id = request.form.get("employee_id")
        name = request.form.get("name")
        qualifications = request.form.getlist("qualification[]")
        experiences = request.form.getlist("experience[]")

        if not emp_id:
            return "Employee ID is required", 400

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


# PDF download feature for personnel info (with search)
@mongo_bp.route('/download', methods=['POST'])
def download_personnel_report():
    search_query = request.form.get("search", "").strip()
    query = {}
    if search_query:
        query["$or"] = [
            {"name": {"$regex": search_query, "$options": "i"}},
            {"employee_id": {"$regex": search_query, "$options": "i"}},
            {"aadhaar": {"$regex": search_query, "$options": "i"}},
            {"pan": {"$regex": search_query, "$options": "i"}},
            {"contact.email": {"$regex": search_query, "$options": "i"}},
            {"contact.phone": {"$regex": search_query, "$options": "i"}}
        ]
    personnel = list(mongo.db.employees_info.find(query))

    html = render_template(
        "personnel_report.html",
        personnel=personnel,
        generated_on=datetime.now().strftime("%Y-%m-%d"),
        generated_time=datetime.now().strftime("%H:%M:%S")
    )

    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if not wkhtmltopdf_path:
        return "wkhtmltopdf not found in container", 500
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    try:
        pdf = pdfkit.from_string(html, False, configuration=config)
    except Exception as e:
        return f"Failed to generate PDF: {e}", 500

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    filename = f"Personnel_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
