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
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    current_salary = db.Column(db.Numeric(10,2))
    previous_salary = db.Column(db.Numeric(10,2))

    professional = db.relationship("ProfessionalInfo", backref="employee", uselist=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class ProfessionalInfo(db.Model):
    __tablename__ = 'professional_info'

    emp_id = db.Column(db.Integer, db.ForeignKey('employee.emp_id'), primary_key=True)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    salary = db.Column(db.Numeric(10, 2))
    last_increment = db.Column(db.Numeric(10, 2))
    skills = db.Column(db.ARRAY(db.Text))
    performance_rating = db.Column(db.Integer)


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.Integer)
    action = db.Column(db.String(20))  # INSERT, UPDATE, DELETE
    table_name = db.Column(db.String(100))
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
