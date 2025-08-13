from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.postgres_models import db
from utils.decorator import login_required
from utils.security import initiate_email_otp_flow, verify_stored_otp
import logging

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

ALLOWED_ROLES = ["user", "viewer", "editor"]

# -------------------------
# Landing page BEFORE login
# -------------------------
@auth_bp.route("/")
def auth_home():
    # Redirect logged-in users to main page
    if session.get("user_id"):
        return redirect(url_for("home"))
    return render_template("auth_home.html")

# -------------------------
# Sign Up
# -------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form.get("role", "user").lower()

        if role not in ALLOWED_ROLES:
            role = "user"

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
        user.password_hash = generate_password_hash(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.signin"))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Signup Error: {e}")
            flash("Failed to create account. Try again later.", "danger")

    return render_template("signup.html")

# -------------------------
# Sign In
# -------------------------
@auth_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        username_or_email = request.form["username_or_email"].strip()
        password = request.form["password"]

        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["role"] = user.role
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("signin.html")

# -------------------------
# Forgot Password
# -------------------------
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email_or_phone"].strip()
        user = User.query.filter(User.email == email).first()

        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("auth.forgot_password"))

        try:
            initiate_email_otp_flow(email)
            session["reset_user_id"] = user.id
            session["reset_email"] = email
            flash("OTP sent to your email. Please verify.", "info")
            return redirect(url_for("auth.verify_otp"))
        except Exception as e:
            logging.error(f"OTP send error: {e}")
            flash("Failed to send OTP. Please try again.", "danger")

    return render_template("forget_password.html")

# -------------------------
# Verify OTP
# -------------------------
@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        email = session.get("reset_email")
        otp_input = request.form["otp"].strip()

        valid, message = verify_stored_otp(email, otp_input)
        if valid:
            session["otp_verified"] = True
            flash("OTP verified! Please set your new password.", "success")
            return redirect(url_for("auth.reset_password"))
        else:
            flash(message, "danger")

    return render_template("otp_verification.html")

# -------------------------
# Reset Password
# -------------------------
@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        if not session.get("otp_verified"):
            flash("Please verify OTP first.", "danger")
            return redirect(url_for("auth.forgot_password"))

        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.reset_password"))

        user_id = session.get("reset_user_id")
        user = User.query.get(user_id)

        if not user:
            flash("Session expired. Please request OTP again.", "danger")
            return redirect(url_for("auth.forgot_password"))

        try:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session.pop("reset_user_id", None)
            session.pop("reset_email", None)
            session.pop("otp_verified", None)
            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("auth.signin"))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Reset Password Error: {e}")
            flash("Failed to update password. Try again.", "danger")

    return render_template("reset_password.html")

# -------------------------
# Profile
# -------------------------
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        try:
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
        except Exception as e:
            db.session.rollback()
            logging.error(f"Profile Update Error: {e}")
            flash("Failed to update profile. Try again.", "danger")

    return render_template("profile.html", user=user)

# -------------------------
# Logout
# -------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.auth_home"))
