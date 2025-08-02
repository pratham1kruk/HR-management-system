from flask import Blueprint, request, render_template, redirect, url_for
from models.postgres_models import db, Employee, ProfessionalInfo

# Define Blueprint with clear name
employee_bp = Blueprint("employee", __name__)

# ─────────────────────────────
# VIEW: List all employees
# ─────────────────────────────
@employee_bp.route("/")
def list_employees():
    employees = Employee.query.all()
    return render_template("employee_list.html", employees=employees)

# ─────────────────────────────
# FORM: Add new employee
# ─────────────────────────────
@employee_bp.route("/new", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        new_emp = Employee(
            emp_id=request.form["emp_id"],
            name=request.form["name"],
            adhar=request.form["adhar"],
            pan=request.form["pan"],
            dependents=int(request.form["dependents"]),
            residence=request.form["residence"]
        )
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html")

# ─────────────────────────────
# FORM: Update employee
# ─────────────────────────────
@employee_bp.route("/edit/<int:emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    if request.method == "POST":
        emp.name = request.form["name"]
        emp.adhar = request.form["adhar"]
        emp.pan = request.form["pan"]
        emp.dependents = int(request.form["dependents"])
        emp.residence = request.form["residence"]
        db.session.commit()
        return redirect(url_for("employee.list_employees"))
    return render_template("employee_form.html", employee=emp)

# ─────────────────────────────
# DELETE: Employee
# ─────────────────────────────
@employee_bp.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for("employee.list_employees"))

# ─────────────────────────────
# ADD/VIEW: Professional Info
# ─────────────────────────────
@employee_bp.route("/<int:emp_id>/professional", methods=["GET", "POST"])
def add_professional(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    if request.method == "POST":
        prof = ProfessionalInfo(
            emp_id=emp_id,
            position=request.form["position"],
            department=request.form["department"],
            salary=float(request.form["salary"]),
            doj=request.form["doj"]
        )
        db.session.add(prof)
        db.session.commit()
        return redirect(url_for("employee.list_employees"))
    return render_template("professional_form.html", employee=emp)
