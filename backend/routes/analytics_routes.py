from flask import Blueprint, render_template, request, make_response
from models.postgres_models import db
from sqlalchemy import text
from datetime import datetime
import pdfkit
import shutil  # ✅ for auto-detecting wkhtmltopdf path

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


# ------------------------------
# Helper function to collect all analytics data
# ------------------------------
def _collect_stats():
    stats = {}

    # 📊 Salary Comparison
    stats["salary_comparison"] = db.session.execute(text("""
        SELECT 
            e.emp_id,
            e.first_name || ' ' || e.last_name AS full_name,
            e.hire_date,
            (p.current_salary - COALESCE(p.previous_salary, 0)) AS salary_diff,
            LAG(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS prev_emp_salary,
            p.current_salary,
            LEAD(p.current_salary, 1) OVER (ORDER BY e.hire_date) AS next_emp_salary,
            p.last_increment
        FROM employee e
        JOIN professional_info p ON e.emp_id = p.emp_id
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

    # 📌 Salary grades
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

    # 📈 Running totals & averages
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

    return stats


# ------------------------------
# Main page
# ------------------------------
@analytics_bp.route("/")
def stats_home():
    stats = _collect_stats()
    return render_template("stats.html", stats=stats)


# ------------------------------
# PDF download route
# ------------------------------
@analytics_bp.route("/download", methods=["POST"])
def download_report():
    company_name = request.form.get("company_name", "Unknown Company")
    company_details = request.form.get("company_details", "")
    stats = _collect_stats()

    current_year = datetime.now().year
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Render HTML for PDF
    html = render_template(
        "stats_report.html",
        stats=stats,
        company_name=company_name,
        company_details=company_details,
        year=current_year,
        generated_at=current_time
    )

    # ✅ Auto-detect wkhtmltopdf path
    wkhtmltopdf_path = shutil.which("wkhtmltopdf")
    if not wkhtmltopdf_path:
        return "wkhtmltopdf not found in container", 500

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Generate PDF
    try:
        pdf = pdfkit.from_string(html, False, configuration=config)
    except Exception as e:
        return f"Failed to generate PDF: {e}", 500

    # Send as download
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    filename = f"HRMS_Report_{current_year}.pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
