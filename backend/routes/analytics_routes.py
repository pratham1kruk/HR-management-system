# routes/analytics_routes.py

from flask import Blueprint, render_template
from models.postgres_models import db
from sqlalchemy import text

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")

@analytics_bp.route("/")
def stats_home():
    stats = {}

    # 📊 Salary Comparison (Lead/Lag + Difference Analysis)
    stats["salary_comparison"] = db.session.execute(text("""
        SELECT 
            e.emp_id,
            e.first_name || ' ' || e.last_name AS full_name,
            e.hire_date,
            -- Salary difference for same employee
            (p.current_salary - COALESCE(p.previous_salary, 0)) AS salary_diff,
            -- Previous employee salary (by hire date)
            LAG(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS prev_emp_salary,
            -- Current employee salary
            p.current_salary,
            -- Next employee salary (by hire date)
            LEAD(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS next_emp_salary,
            -- Last increment
            p.last_increment
        FROM employee e
        JOIN professional_info p 
            ON e.emp_id = p.emp_id
        ORDER BY e.hire_date
    """)).fetchall()

    # 🏆 Top earners
    stats["top_earners"] = db.session.execute(
        text("SELECT * FROM top_earners_per_department")
    ).fetchall()

    # ⚠️ Low performers
    stats["low_performers"] = db.session.execute(
        text("SELECT * FROM low_performers")
    ).fetchall()

    # 🚀 Promotion candidates
    stats["promotion_candidates"] = db.session.execute(
        text("SELECT * FROM promotion_candidates")
    ).fetchall()

    # 🎯 Experienced employees
    stats["experienced_employees"] = db.session.execute(
        text("SELECT * FROM experienced_employees")
    ).fetchall()

    # 📌 Salary grades (CASE logic)
    stats["salary_grades"] = db.session.execute(text("""
        SELECT emp_id, department, current_salary,
        CASE 
            WHEN current_salary > 70000 THEN 'High'
            WHEN current_salary BETWEEN 50000 AND 70000 THEN 'Medium'
            ELSE 'Low'
        END AS grade
        FROM professional_info
    """)).fetchall()

    # 🥇 Salary rank
    stats["salary_ranks"] = db.session.execute(text("""
        SELECT emp_id, current_salary,
        RANK() OVER (ORDER BY current_salary DESC) AS salary_rank
        FROM professional_info
    """)).fetchall()

    # 📈 Running totals and averages
    stats["running_salary"] = db.session.execute(text("""
        SELECT emp_id, current_salary,
        SUM(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_sum,
        AVG(current_salary) OVER (ORDER BY emp_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_avg
        FROM professional_info
    """)).fetchall()

    # 🏢 Departments with salary above average
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
