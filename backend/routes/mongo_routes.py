from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from bson.objectid import ObjectId
from app import mongo

mongo_bp = Blueprint('mongo', __name__, url_prefix='/personnel')

# ─────────────────────────────
# VIEW: List all personnel info
# ─────────────────────────────
@mongo_bp.route('/')
def list_personnel():
    personnel = list(mongo.db.employees_info.find())
    return render_template('personnel_info.html', personnel=personnel)

# ─────────────────────────────
# FORM: Add new personnel info
# ─────────────────────────────
@mongo_bp.route('/add', methods=['GET', 'POST'])
def add_personnel():
    if request.method == 'POST':
        data = {
            "emp_id": request.form.get("emp_id"),
            "permanent_address": request.form.get("permanent_address"),
            "current_address": request.form.get("current_address"),
            "emergency_contact": request.form.get("emergency_contact"),
            "blood_group": request.form.get("blood_group")
        }
        mongo.db.employees_info.insert_one(data)
        return redirect(url_for('mongo.list_personnel'))
    return render_template('personnel_form.html')

# ─────────────────────────────
# FORM: Update personnel info
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
        updated_data = {
            "emp_id": request.form.get("emp_id"),
            "permanent_address": request.form.get("permanent_address"),
            "current_address": request.form.get("current_address"),
            "emergency_contact": request.form.get("emergency_contact"),
            "blood_group": request.form.get("blood_group")
        }
        mongo.db.employees_info.update_one({"_id": obj_id}, {"$set": updated_data})
        return redirect(url_for('mongo.list_personnel'))
    
    return render_template('personnel_form.html', data=existing)

# ─────────────────────────────
# DELETE: Personnel record
# ─────────────────────────────
@mongo_bp.route('/delete/<id>', methods=['GET'])
def delete_personnel(id):
    try:
        obj_id = ObjectId(id)
        mongo.db.employees_info.delete_one({"_id": obj_id})
    except Exception:
        return "Invalid ID", 400
    return redirect(url_for('mongo.list_personnel'))

# ─────────────────────────────
# VIEW: Single personnel JSON
# ─────────────────────────────
@mongo_bp.route('/<id>', methods=['GET'])
def view_personnel(id):
    try:
        obj_id = ObjectId(id)
        person = mongo.db.employees_info.find_one({"_id": obj_id})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400

    if not person:
        return jsonify({"error": "Not found"}), 404

    person["_id"] = str(person["_id"])
    return jsonify(person)
