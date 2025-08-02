from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from bson.objectid import ObjectId
from models.mongo_models import personnel_collection

mongo_bp = Blueprint('mongo', __name__, url_prefix='/personnel')

# Show all personnel info from MongoDB
@mongo_bp.route('/')
def list_personnel():
    personnel = list(personnel_collection.find())
    return render_template('personnel_info.html', personnel=personnel)

# Show form to add new personnel info
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
        personnel_collection.insert_one(data)
        return redirect(url_for('mongo.list_personnel'))
    return render_template('personnel_form.html')

# Update personnel info by _id
@mongo_bp.route('/update/<id>', methods=['GET', 'POST'])
def update_personnel(id):
    existing = personnel_collection.find_one({"_id": ObjectId(id)})
    if not existing:
        return "Not found", 404

    if request.method == 'POST':
        new_data = {
            "emp_id": request.form.get("emp_id"),
            "permanent_address": request.form.get("permanent_address"),
            "current_address": request.form.get("current_address"),
            "emergency_contact": request.form.get("emergency_contact"),
            "blood_group": request.form.get("blood_group")
        }
        personnel_collection.update_one({"_id": ObjectId(id)}, {"$set": new_data})
        return redirect(url_for('mongo.list_personnel'))
    
    return render_template('personnel_form.html', data=existing)

# Delete personnel record
@mongo_bp.route('/delete/<id>')
def delete_personnel(id):
    personnel_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('mongo.list_personnel'))

# Get a single personnel record as JSON
@mongo_bp.route('/<id>')
def view_personnel(id):
    person = personnel_collection.find_one({"_id": ObjectId(id)})
    if not person:
        return jsonify({"error": "Not found"}), 404
    person["_id"] = str(person["_id"])  # Convert ObjectId to string
    return jsonify(person)
