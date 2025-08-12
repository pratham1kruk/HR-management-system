# routes/mongo_analytics_routes.py
from flask import Blueprint, render_template, request, make_response, current_app, abort, flash, redirect, url_for
from app import mongo    # <- uses the same 'mongo' you already created in your app
import pdfkit
import shutil
from datetime import datetime
from pytz import timezone

mongo_analytics_bp = Blueprint("mongo_analytics", __name__, url_prefix="/personnel/analytics")

# ----------------------------
# Helper: collect Mongo analytics
# ----------------------------
def _collect_mongo_stats():
    db = mongo.db

    # Blood group counts
    blood_pipeline = [
        {"$group": {"_id": "$blood_group", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    blood_data = list(db.employees_info.aggregate(blood_pipeline))

    # Qualifications summary (from 'qualifications' collection or embedded; we handle both)
    # We expect qualification documents in either a 'qualifications' collection or inside employees_info
    qualification_data = []
    try:
        # If there's a qualifications collection (as earlier in your routes)
        qualification_data = list(db.qualifications.aggregate([
            {"$project": {"_id": "$employee_id", "name": "$name", "qualifications": "$qualifications", "experiences": "$experiences", "count": {"$size": {"$ifNull": ["$qualifications", []]}}}},
            {"$sort": {"count": -1}}
        ]))
    except Exception:
        qualification_data = []

    # fallback: build from employees_info if qualifications not separate
    if not qualification_data:
        # look for array fields inside employees_info
        q_pipeline = [
            {"$project": {
                "_id": "$employee_id",
                "name": "$name",
                "qualifications": "$qualifications",
                "experiences": "$experiences",
                "count": {"$size": {"$ifNull": ["$qualifications", []]}}
            }},
            {"$sort": {"count": -1}}
        ]
        qualification_data = list(db.employees_info.aggregate(q_pipeline))

    # City-wise distribution
    city_pipeline = [
        {"$group": {"_id": "$residence.city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    city_data = list(db.employees_info.aggregate(city_pipeline))

    # State-wise distribution
    state_pipeline = [
        {"$group": {"_id": "$residence.state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_data = list(db.employees_info.aggregate(state_pipeline))

    # Gender distribution (counts + percent)
    total_count = db.employees_info.count_documents({})
    male_count = db.employees_info.count_documents({"gender": "Male"})
    female_count = db.employees_info.count_documents({"gender": "Female"})
    gender_stats = {
        "male": male_count,
        "female": female_count,
        "male_percent": round((male_count / total_count * 100), 2) if total_count else 0,
        "female_percent": round((female_count / total_count * 100), 2) if total_count else 0,
        "total": total_count
    }

    stats = {
        "blood_data": blood_data,
        "qualification_data": qualification_data,
        "city_data": city_data,
        "state_data": state_data,
        "gender_stats": gender_stats
    }
    return stats

# ----------------------------
# Page: mongo stats (tabbed if you want to combine later)
# ----------------------------
@mongo_analytics_bp.route("/")
def mongo_stats_home():
    stats = _collect_mongo_stats()
    # pass to template
    return render_template("mongo_stats.html", **stats)


# ----------------------------
# POST: download PDF report
# ----------------------------
@mongo_analytics_bp.route("/download", methods=["POST"])
def mongo_download_report():
    # form data
    company_name = request.form.get("company_name", "").strip() or "Unknown Company"
    company_details = request.form.get("company_details", "").strip() or ""

    # 🕒 Generate Indian date and time
    india_tz = timezone("Asia/Kolkata")
    now_ist = datetime.now(india_tz)
    generated_on = now_ist.strftime("%Y-%m-%d")
    generated_time = now_ist.strftime("%H:%M:%S")

    stats = _collect_mongo_stats()

    # Render report HTML
    html = render_template(
        "mongo_stats_report.html",
        company_name=company_name,
        company_details=company_details,
        generated_on=generated_on,
        generated_time=generated_time,
        **stats
    )

    # Find wkhtmltopdf binary using shutil.which
    wk_path = shutil.which("wkhtmltopdf")
    if wk_path is None:
        alt_path = "/usr/local/bin/wkhtmltopdf"
        if shutil.which(alt_path):
            wk_path = alt_path

    if wk_path is None:
        flash("wkhtmltopdf not found in container. Install it or provide its path. PDF generation unavailable.", "danger")
        return redirect(url_for("mongo_analytics.mongo_stats_home"))

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=wk_path)
    options = {
        "page-size": "A4",
        "encoding": "UTF-8",
        "quiet": "",
        "margin-top": "15mm",
        "margin-bottom": "15mm",
        "margin-left": "12mm",
        "margin-right": "12mm",
        "enable-local-file-access": None
    }

    try:
        pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    except Exception as e:
        current_app.logger.exception("Failed to generate PDF")
        flash(f"Failed to generate PDF: {e}", "danger")
        return redirect(url_for("mongo_analytics.mongo_stats_home"))

    # Send PDF as response
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    filename = f"Mongo_Analytics_Report_{now_ist.strftime('%Y%m%d_%H%M')}.pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response