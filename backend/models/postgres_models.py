# backend/models/postgres_models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employee'
    emp_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(15))
    hire_date = db.Column(db.Date, default=datetime.utcnow)

    professional = db.relationship("ProfessionalInfo", backref="employee", uselist=False)

class ProfessionalInfo(db.Model):
    __tablename__ = 'professional_info'
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), nullable=False)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    salary = db.Column(db.Float)
    last_review_date = db.Column(db.Date)

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    action = db.Column(db.String(20))  # INSERT, UPDATE, DELETE
    table_name = db.Column(db.String(100))
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
