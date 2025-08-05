from flask import Blueprint, render_template
from models.postgres_models import db
from sqlalchemy import text

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

# ─────────────────────────────
# Analytics Homepage
# ─────────────────────────────
@analytics_bp.route("/")
def stats_home():
    stats = {}

    # 1. Top earners per department
    stats["top_earners"] = db.session.execute(text("SELECT * FROM top_earners_per_department")).fetchall()

    # 2. Low performers
    stats["low_performers"] = db.session.execute(text("SELECT * FROM low_performers")).fetchall()

    # 3. Promotion candidates
    stats["promotion_candidates"] = db.session.execute(text("SELECT * FROM promotion_candidates")).fetchall()

    # 4. Experienced employees (>3 years)
    stats["experienced"] = db.session.execute(text("SELECT * FROM experienced_employees")).fetchall()

    # 5. Salary Grades
    stats["grades"] = db.session.execute(text("""
        SELECT emp_id, department, salary,
        CASE 
            WHEN salary > 70000 THEN 'High'
            WHEN salary BETWEEN 50000 AND 70000 THEN 'Medium'
            ELSE 'Low'
        END AS grade
        FROM professional_info
    """)).fetchall()

    # 6. Rank by salary
    stats["salary_ranks"] = db.session.execute(text("""
        SELECT emp_id, salary,
        RANK() OVER (ORDER BY salary DESC) AS rank
        FROM professional_info
    """)).fetchall()

    # 7. Running salary sum & avg
    stats["salary_running"] = db.session.execute(text("""
        SELECT emp_id, salary,
        SUM(salary) OVER (ORDER BY emp_id) AS running_sum,
        AVG(salary) OVER (ORDER BY emp_id) AS running_avg
        FROM professional_info
    """)).fetchall()

    return render_template("stats.html", stats=stats)