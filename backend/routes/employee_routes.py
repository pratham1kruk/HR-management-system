# ────── employee_routes.py ──────
from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.postgres_models import db, Employee, ProfessionalInfo
from datetime import datetime

employee_bp = Blueprint("employee", __name__, url_prefix="/employees")

@employee_bp.route("/")
def list_employees():
    employees = db.session.query(Employee).outerjoin(ProfessionalInfo).all()
    return render_template("employee_list.html", employees=employees)

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
            hire_date=datetime.strptime(request.form["hire_date"], "%Y-%m-%d"),
        )
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html")

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
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html", employee=emp)

@employee_bp.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for("employee.list_employees"))

@employee_bp.route("/<int:emp_id>/professional", methods=["GET", "POST"])
def add_update_professional(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()

    if request.method == "POST":
        if prof:
            prof.department = request.form["department"]
            prof.designation = request.form["designation"]
            prof.current_salary = float(request.form["current_salary"])
            prof.previous_salary = float(request.form["previous_salary"])
        else:
            prof = ProfessionalInfo(
                emp_id=emp_id,
                department=request.form["department"],
                designation=request.form["designation"],
                current_salary=float(request.form["current_salary"]),
                previous_salary=float(request.form["previous_salary"])
            )
            db.session.add(prof)
        db.session.commit()
        return redirect(url_for("employee.list_employees"))

    return render_template("professional_form.html", employee=emp, professional=prof)

@employee_bp.route("/<int:emp_id>/professional/delete", methods=["POST"])
def delete_professional(emp_id):
    prof = ProfessionalInfo.query.filter_by(emp_id=emp_id).first()
    if prof:
        db.session.delete(prof)
        db.session.commit()
        flash("Professional Info deleted.")
    return redirect(url_for("employee.list_employees"))