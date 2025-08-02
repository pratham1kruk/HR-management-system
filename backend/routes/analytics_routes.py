from flask import Blueprint, render_template
from sqlalchemy import func, desc
from models.postgres_models import db, Employee, ProfessionalInfo
from models.mongo_models import get_personnel_collection

analytics_bp = Blueprint('analytics', __name__)

# 1. Average salary by department
@analytics_bp.route("/avg-salary")
def avg_salary_by_dept():
    data = (
        db.session.query(
            Employee.department,
            func.avg(ProfessionalInfo.salary).label('avg_salary')
        )
        .join(ProfessionalInfo, Employee.id == ProfessionalInfo.emp_id)
        .group_by(Employee.department)
        .all()
    )
    return render_template(
        "stats.html",
        title="Average Salary by Department",
        data=data,
        label1="Department",
        label2="Average Salary"
    )

# 2. Top performers by score
@analytics_bp.route("/top-performers")
def top_performers():
    data = (
        db.session.query(
            Employee.name,
            ProfessionalInfo.performance_score
        )
        .join(ProfessionalInfo, Employee.id == ProfessionalInfo.emp_id)
        .order_by(desc(ProfessionalInfo.performance_score))
        .limit(10)
        .all()
    )
    return render_template(
        "stats.html",
        title="Top 10 Performers",
        data=data,
        label1="Name",
        label2="Score"
    )

# 3. Recently joined employees
@analytics_bp.route("/recent-hires")
def recent_joins():
    data = (
        db.session.query(
            Employee.name,
            Employee.hire_date
        )
        .order_by(desc(Employee.hire_date))
        .limit(10)
        .all()
    )
    return render_template(
        "stats.html",
        title="Recent Hires",
        data=data,
        label1="Name",
        label2="Hire Date"
    )

# 4. MongoDB: Employees missing PAN
@analytics_bp.route("/missing-pan")
def mongo_missing_pan():
    collection = get_personnel_collection()
    results = collection.find({"pan": {"$exists": False}})
    data = [(doc.get("name", "N/A"), str(doc.get("_id"))) for doc in results]
    return render_template(
        "stats.html",
        title="Employees Missing PAN (MongoDB)",
        data=data,
        label1="Name",
        label2="Mongo ID"
    )

# 5. MongoDB: Count by qualification
@analytics_bp.route("/qualification-count")
def qualification_counts():
    collection = get_personnel_collection()
    pipeline = [
        {"$group": {"_id": "$qualification", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = collection.aggregate(pipeline)
    data = [(doc["_id"] or "N/A", doc["count"]) for doc in results]
    return render_template(
        "stats.html",
        title="Personnel Count by Qualification",
        data=data,
        label1="Qualification",
        label2="Count"
    )
