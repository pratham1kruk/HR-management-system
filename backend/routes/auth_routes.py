from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from models.postgres_models import db
from utils.security import generate_otp, send_email_otp, send_sms_otp
from utils.decorator import login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# -----------------------------
# Home page for auth (optional landing)
# -----------------------------
@auth_bp.route("/home")
def auth_home():
    return render_template("auth_home.html")

# -----------------------------
# Sign Up / Register
# -----------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form.get("role", "user")
        
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.signup"))
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists!", "danger")
            return redirect(url_for("auth.signup"))

        user = User(
            username=username,
            email=email,
            role=role,
            first_name=request.form.get("first_name"),
            last_name=request.form.get("last_name"),
            job_title=request.form.get("job_title"),
            work_phone=request.form.get("work_phone"),
            company_name=request.form.get("company_name"),
            country=request.form.get("country"),
            address=request.form.get("address"),
            city=request.form.get("city"),
            state=request.form.get("state"),
            zip_code=request.form.get("zip_code")
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.signin"))

    return render_template("signup.html")

# -----------------------------
# Sign In / Login
# -----------------------------
@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username_or_email = request.form["username_or_email"]
        password = request.form["password"]
        user = User.query.filter((User.username == username_or_email) |
                                 (User.email == username_or_email)).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["role"] = user.role
            flash("Logged in successfully!", "success")
            return redirect(url_for("auth.auth_home"))
        flash("Invalid credentials!", "danger")
        return redirect(url_for("auth.signin"))

    return render_template("signin.html")

# -----------------------------
# Forgot Password
# -----------------------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email_or_phone = request.form["email_or_phone"]
        user = User.query.filter((User.email == email_or_phone) |
                                 (User.work_phone == email_or_phone)).first()
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("auth.forgot_password"))

        otp = generate_otp()
        session["otp"] = otp
        session["reset_user_id"] = user.id

        if "@" in email_or_phone:
            send_email_otp(email_or_phone, otp)
        else:
            send_sms_otp(email_or_phone, otp)

        flash("OTP sent! Please verify.", "info")
        return redirect(url_for("auth.verify_otp"))

    return render_template("forget_password.html")

# -----------------------------
# OTP Verification
# -----------------------------
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp_input = request.form["otp"]
        if otp_input == session.get("otp"):
            flash("OTP verified! Set your new password.", "success")
            return redirect(url_for("auth.reset_password"))
        flash("Invalid OTP!", "danger")
        return redirect(url_for("auth.verify_otp"))

    return render_template("otp_verification.html")

# -----------------------------
# Reset Password
# -----------------------------
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.reset_password"))

        user_id = session.get("reset_user_id")
        user = User.query.get(user_id)
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash("Password updated successfully! Please login.", "success")
            session.pop("otp", None)
            session.pop("reset_user_id", None)
            return redirect(url_for("auth.signin"))

    return render_template("reset_password.html")

# -----------------------------
# Profile
# -----------------------------
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.job_title = request.form.get("job_title")
        user.work_phone = request.form.get("work_phone")
        user.company_name = request.form.get("company_name")
        user.country = request.form.get("country")
        user.address = request.form.get("address")
        user.city = request.form.get("city")
        user.state = request.form.get("state")
        user.zip_code = request.form.get("zip_code")
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("profile.html", user=user)

# -----------------------------
# Logout
# -----------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.signin"))
