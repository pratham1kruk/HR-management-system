from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.postgres_models import db, Employee, ProfessionalInfo

employee_bp = Blueprint("employee", __name__)

# ─────────────────────────────
# VIEW: List all employees with professional info
# ─────────────────────────────
@employee_bp.route("/")
def list_employees():
    employees = db.session.query(Employee).outerjoin(ProfessionalInfo).all()
    return render_template("employee_list.html", employees=employees)

# ─────────────────────────────
# FORM: Add new employee (basic info only)
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
# FORM: Update employee basic info
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
# ADD/UPDATE Professional Info
# ─────────────────────────────
@employee_bp.route("/<int:emp_id>/professional", methods=["GET", "POST"])
def add_update_professional(emp_id):
    emp = Employee.query.get_or_404(emp_id)
    prof = ProfessionalInfo.query.get(emp_id)

    if request.method == "POST":
        if prof:
            # Update existing
            prof.department = request.form["department"]
            prof.designation = request.form["designation"]
            prof.experience = int(request.form["experience"])
            prof.salary = float(request.form["salary"])
            prof.last_increment = float(request.form["last_increment"])
            prof.skills = request.form.get("skills").split(',')
            prof.performance_rating = int(request.form["performance_rating"])
        else:
            # Add new
            prof = ProfessionalInfo(
                emp_id=emp_id,
                department=request.form["department"],
                designation=request.form["designation"],
                experience=int(request.form["experience"]),
                salary=float(request.form["salary"]),
                last_increment=float(request.form["last_increment"]),
                skills=request.form.get("skills").split(','),
                performance_rating=int(request.form["performance_rating"])
            )
            db.session.add(prof)
        db.session.commit()
        return redirect(url_for("employee.list_employees"))

    return render_template("professional_form.html", employee=emp, professional=prof)

# ─────────────────────────────
# DELETE: Professional Info
# ─────────────────────────────
@employee_bp.route("/<int:emp_id>/professional/delete", methods=["POST"])
def delete_professional(emp_id):
    prof = ProfessionalInfo.query.get_or_404(emp_id)
    db.session.delete(prof)
    db.session.commit()
    flash("Professional Info deleted.")
    return redirect(url_for("employee.list_employees"))
