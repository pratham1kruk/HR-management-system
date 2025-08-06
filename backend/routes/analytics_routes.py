# routes/analytics_routes.py

from flask import Blueprint, render_template
from models.postgres_models import db
from sqlalchemy import text

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/")
def stats_home():
    stats = {}

    # Views
    stats["top_earners"] = db.session.execute(text("SELECT * FROM top_earners_per_department")).fetchall()
    stats["low_performers"] = db.session.execute(text("SELECT * FROM low_performers")).fetchall()
    stats["promotion_candidates"] = db.session.execute(text("SELECT * FROM promotion_candidates")).fetchall()
    stats["experienced_employees"] = db.session.execute(text("SELECT * FROM experienced_employees")).fetchall()

    # CASE-based salary grades
    stats["salary_grades"] = db.session.execute(text("""
        SELECT emp_id, department, current_salary,
        CASE 
            WHEN current_salary > 70000 THEN 'High'
            WHEN current_salary BETWEEN 50000 AND 70000 THEN 'Medium'
            ELSE 'Low'
        END AS grade
        FROM professional_info
    """)).fetchall()

    # RANK by salary
    stats["salary_ranks"] = db.session.execute(text("""
        SELECT emp_id, current_salary,
        RANK() OVER (ORDER BY current_salary DESC) AS salary_rank
        FROM professional_info
    """)).fetchall()

    # Running salary stats
    stats["running_salary"] = db.session.execute(text("""
        SELECT emp_id, current_salary,
        SUM(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sum,
        AVG(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_avg
        FROM professional_info
    """)).fetchall()

    # LEAD & LAG salaries
    stats["salary_lead_lag"] = db.session.execute(text("""
        SELECT emp_id, current_salary, last_increment,
        LAG(current_salary) OVER (ORDER BY emp_id) AS previous_salary,
        LEAD(current_salary) OVER (ORDER BY emp_id) AS next_salary
        FROM professional_info
    """)).fetchall()

    # Avg salary comparison with department
    stats["departments_above_avg"] = db.session.execute(text("""
        WITH dept_avg AS (
            SELECT department, AVG(current_salary) AS dept_avg_salary
            FROM professional_info
            GROUP BY department
        ), overall_avg AS (
            SELECT AVG(current_salary) AS overall_salary
            FROM professional_info
        )
        SELECT d.*
        FROM dept_avg d, overall_avg o
        WHERE d.dept_avg_salary > o.overall_salary
    """)).fetchall()

    return render_template("stats.html", stats=stats)
