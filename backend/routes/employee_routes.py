from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.postgres_models import db, Employee, ProfessionalInfo
from datetime import datetime

employee_bp = Blueprint("employee", __name__, url_prefix="/employees")


# Employee home menu
@employee_bp.route("/home")
def employee_home():
    return render_template("employee_home.html")


# Original list (unchanged for safety)
@employee_bp.route("/")
def list_employees():
    employees = Employee.query.all()
    return render_template("employee_list.html", employees=employees)


# NEW: Tabbed View for General + Professional Info
@employee_bp.route("/tabbed")
def list_employees_tabbed():
    employees = Employee.query.outerjoin(ProfessionalInfo).all()
    return render_template("employee_tabbed.html", employees=employees)


# Add basic general info
@employee_bp.route("/new", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        new_emp = Employee(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            dob=request.form["dob"],
            gender=request.form["gender"],
            email=request.form["email"],
            phone=request.form["phone"],
            hire_date=datetime.strptime(request.form["hire_date"], "%Y-%m-%d")
        )
        db.session.add(new_emp)
        db.session.commit()
        flash("Employee general info added successfully.")
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html")


# Add professional info
@employee_bp.route("/professional", methods=["GET", "POST"])
def add_professional_info():
    if request.method == "POST":
        emp_id = int(request.form["emp_id"])
        if ProfessionalInfo.query.filter_by(emp_id=emp_id).first():
            flash("Professional info already exists. Please edit instead.")
            return redirect(url_for("employee.list_employees"))

        prof = ProfessionalInfo(
            emp_id=emp_id,
            designation=request.form["designation"],
            department=request.form["department"],
            current_salary=float(request.form["current_salary"]),
            previous_salary=float(request.form["previous_salary"]),
            last_increment=float(request.form["last_increment"]),
            skills=[s.strip() for s in request.form["skills"].split(",") if s.strip()],
            performance_rating=float(request.form["performance_rating"])
        )
        db.session.add(prof)
        db.session.commit()
        flash("Professional info added successfully.")
        return redirect(url_for("employee.list_employees"))

    emp_id = request.args.get("emp_id", type=int)
    return render_template("professional_form.html", emp_id=emp_id)


# Edit general info
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
        flash("Employee general info updated.")
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html", employee=emp)


# Edit professional info
@employee_bp.route("/edit/professional/<int:emp_id>", methods=["GET", "POST"])
def edit_professional(emp_id):
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()
    if not prof:
        flash("No professional info found. Please add it first.")
        return redirect(url_for("employee.add_professional_info", emp_id=emp_id))

    if request.method == "POST":
        prof.designation = request.form["designation"]
        prof.department = request.form["department"]
        prof.current_salary = float(request.form["current_salary"])
        prof.previous_salary = float(request.form["previous_salary"])
        prof.last_increment = float(request.form["last_increment"])
        prof.skills = [s.strip() for s in request.form["skills"].split(",") if s.strip()]
        prof.performance_rating = float(request.form["performance_rating"])
        db.session.commit()
        flash("Professional info updated.")
        return redirect(url_for("employee.list_employees"))

    return render_template("professional_form.html", professional=prof, emp_id=emp_id)


# Delete employee + professional info
@employee_bp.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee and related professional info deleted.")
    return redirect(url_for("employee.list_employees"))
