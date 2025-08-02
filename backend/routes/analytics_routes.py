from flask import Blueprint, render_template
from sqlalchemy import func, desc
from models.postgres_models import db, Employee, ProfessionalInfo
from models.mongo_models import get_personnel_collection

analytics_bp = Blueprint('analytics', __name__, url_prefix="/analytics")

@analytics_bp.route("/")
def analytics_dashboard():
    cursor = db.session.connection()

    # SQL Analytics
    exp_emp = cursor.execute("SELECT * FROM experienced_employees").fetchall()
    low_perf = cursor.execute("SELECT * FROM low_performers").fetchall()
    promo = cursor.execute("SELECT * FROM promotion_candidates").fetchall()
    top_earners = cursor.execute("SELECT * FROM top_earners_per_department").fetchall()

    above_avg = cursor.execute("""
        WITH dept_avg AS (
            SELECT department, AVG(salary) AS dept_avg_salary
            FROM professional_info GROUP BY department
        ), overall_avg AS (
            SELECT AVG(salary) AS overall_salary
            FROM professional_info
        )
        SELECT d.*
        FROM dept_avg d, overall_avg o
        WHERE d.dept_avg_salary > o.overall_salary
    """).fetchall()

    lead_lag = cursor.execute("""
        SELECT emp_id, salary, last_increment,
               LAG(salary) OVER (ORDER BY emp_id) AS prev_salary,
               LEAD(salary) OVER (ORDER BY emp_id) AS next_salary
        FROM professional_info
    """).fetchall()

    running_salary = cursor.execute("""
        SELECT emp_id, salary,
               SUM(salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_sum,
               AVG(salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_salary_avg
        FROM professional_info
    """).fetchall()

    rank = cursor.execute("""
        SELECT emp_id, salary,
               RANK() OVER (ORDER BY salary DESC) AS salary_rank
        FROM professional_info
    """).fetchall()

    salary_grade = cursor.execute("""
        SELECT emp_id, department, salary,
            CASE 
                WHEN salary > 70000 THEN 'High'
                WHEN salary BETWEEN 50000 AND 70000 THEN 'Medium'
                ELSE 'Low'
            END AS salary_grade
        FROM professional_info
    """).fetchall()

    # Mongo Analytics
    collection = get_personnel_collection()
    missing_pan = collection.find({"pan": {"$exists": False}})
    missing_pan_data = [(doc.get("name", "N/A"), str(doc["_id"])) for doc in missing_pan]

    pipeline = [
        {"$group": {"_id": "$qualification", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    qualification_counts = collection.aggregate(pipeline)
    qualification_data = [(doc["_id"], doc["count"]) for doc in qualification_counts]

    return render_template("stats.html",
        exp_emp=exp_emp,
        low_perf=low_perf,
        promo=promo,
        top_earners=top_earners,
        above_avg=above_avg,
        lead_lag=lead_lag,
        running_salary=running_salary,
        rank=rank,
        salary_grade=salary_grade,
        missing_pan_data=missing_pan_data,
        qualification_data=qualification_data
    )