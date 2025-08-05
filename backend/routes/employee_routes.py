from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.postgres_models import db, Employee, ProfessionalInfo
from datetime import datetime

employee_bp = Blueprint("employee", __name__, url_prefix="/employees")

# ─────────────────────────────
# HOME PAGE: Employee Menu
# ─────────────────────────────
@employee_bp.route("/home")
def employee_home():
    return render_template("employee_home.html")

# ─────────────────────────────
# VIEW: List all employees
# ─────────────────────────────
@employee_bp.route("/")
def list_employees():
    employees = db.session.query(Employee).outerjoin(ProfessionalInfo).all()
    return render_template("employee_list.html", employees=employees)

# ─────────────────────────────
# ADD: Basic Employee Info
# ─────────────────────────────
@employee_bp.route("/new", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        new_emp = Employee(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            dob=request.form.get("dob"),
            gender=request.form.get("gender"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            hire_date=datetime.strptime(request.form["hire_date"], "%Y-%m-%d")
        )
        db.session.add(new_emp)
        db.session.commit()
        flash("Employee added.")
        return redirect(url_for("employee.employee_home"))
    return render_template("employee_form.html")

# ─────────────────────────────
# ADD: Professional Info
# ─────────────────────────────
@employee_bp.route("/professional", methods=["GET", "POST"])
def add_professional_info():
    if request.method == "POST":
        emp_id = int(request.form["emp_id"])
        existing = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()

        if existing:
            flash("Professional info already exists. Use edit instead.")
            return redirect(url_for("employee.list_employees"))

        prof = ProfessionalInfo(
            emp_id=emp_id,
            designation=request.form["designation"],
            department=request.form["department"],
            experience=int(request.form["experience"]),
            salary=float(request.form["salary"]),
            last_increment=float(request.form["last_increment"]),
            skills=request.form.getlist("skills"),  # checkbox or multi-select
            performance_rating=int(request.form["performance_rating"])
        )
        db.session.add(prof)
        db.session.commit()
        flash("Professional info added.")
        return redirect(url_for("employee.list_employees"))

    return render_template("professional_form.html", professional=None)

# ─────────────────────────────
# EDIT: Employee Info
# ─────────────────────────────
@employee_bp.route("/edit/<int:emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    if request.method == "POST":
        emp.first_name = request.form["first_name"]
        emp.last_name = request.form["last_name"]
        emp.dob = request.form["dob"]
        emp.gender = request.form["gender"]
        emp.email = request.form["email"]
        emp.phone = request.form["phone"]
        emp.hire_date = datetime.strptime(request.form["hire_date"], "%Y-%m-%d")
        db.session.commit()
        flash("Employee updated.")
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html", employee=emp)

# ─────────────────────────────
# EDIT: Professional Info
# ─────────────────────────────
@employee_bp.route("/edit/professional/<int:emp_id>", methods=["GET", "POST"])
def edit_professional(emp_id):
    prof = ProfessionalInfo.query.get_or_404(emp_id)
    if request.method == "POST":
        prof.department = request.form["department"]
        prof.designation = request.form["designation"]
        prof.experience = int(request.form["experience"])
        prof.salary = float(request.form["salary"])
        prof.last_increment = float(request.form["last_increment"])
        prof.skills = request.form.getlist("skills")
        prof.performance_rating = int(request.form["performance_rating"])
        db.session.commit()
        flash("Professional info updated.")
        return redirect(url_for("employee.list_employees"))
    return render_template("professional_form.html", professional=prof)

# ─────────────────────────────
# DELETE: Employee & Professional
# ─────────────────────────────
@employee_bp.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()
    if prof:
        db.session.delete(prof)
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee and professional info deleted.")
    return redirect(url_for("employee.list_employees"))
