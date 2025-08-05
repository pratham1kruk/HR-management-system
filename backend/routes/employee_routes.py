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
# VIEW: List all employees with joined professional info
# ─────────────────────────────
@employee_bp.route("/")
def list_employees():
    employees = db.session.query(Employee).outerjoin(ProfessionalInfo).all()
    return render_template("employee_list.html", employees=employees)


# ─────────────────────────────
# ADD: Basic Employee Info only
# ─────────────────────────────
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
        flash("Employee basic info added.")
        return redirect(url_for("employee.employee_home"))
    return render_template("employee_form.html")


# ─────────────────────────────
# ADD: Professional Info only using emp_id
# ─────────────────────────────
@employee_bp.route("/professional", methods=["GET", "POST"])
def add_professional_info():
    if request.method == "POST":
        emp_id = int(request.form["emp_id"])
        existing_prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()

        if existing_prof:
            flash("Professional info already exists for this employee. Use list view to update.")
            return redirect(url_for("employee.list_employees"))

        prof = ProfessionalInfo(
            emp_id=emp_id,
            department=request.form["department"],
            designation=request.form["designation"],
            current_salary=float(request.form["current_salary"]),
            previous_salary=float(request.form["previous_salary"])
        )
        db.session.add(prof)
        db.session.commit()
        flash("Professional info added.")
        return redirect(url_for("employee.employee_home"))
    
    return render_template("professional_form.html")


# ─────────────────────────────
# EDIT: General Info via list
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
        flash("Employee info updated.")
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html", employee=emp)


# ─────────────────────────────
# EDIT: Professional Info via list
# ─────────────────────────────
@employee_bp.route("/edit/professional/<int:emp_id>", methods=["GET", "POST"])
def edit_professional(emp_id):
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first_or_404()
    if request.method == "POST":
        prof.department = request.form["department"]
        prof.designation = request.form["designation"]
        prof.current_salary = float(request.form["current_salary"])
        prof.previous_salary = float(request.form["previous_salary"])
        db.session.commit()
        flash("Professional info updated.")
        return redirect(url_for("employee.list_employees"))
    return render_template("professional_form.html", professional=prof)


# ─────────────────────────────
# DELETE: Entire Employee record
# ─────────────────────────────
@employee_bp.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()
    if prof:
        db.session.delete(prof)

    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash("Employee and related professional info deleted.")
    return redirect(url_for("employee.list_employees"))
