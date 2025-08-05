from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employee'

    emp_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    hire_date = db.Column(db.Date, default=datetime.utcnow)

    professional = db.relationship("ProfessionalInfo", backref="employee", uselist=False)

class ProfessionalInfo(db.Model):
    __tablename__ = 'professional_info'

    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), primary_key=True)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    current_salary = db.Column(db.Numeric(10, 2))
    previous_salary = db.Column(db.Numeric(10, 2))
    last_increment = db.Column(db.Numeric(10, 2))
    skills = db.Column(db.ARRAY(db.Text))
    performance_rating = db.Column(db.Float)

class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    action = db.Column(db.String(20))
    table_name = db.Column(db.String(100))
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
