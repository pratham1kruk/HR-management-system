from functools import wraps
from flask import session, redirect, url_for, flash

# -----------------------------
# Login Required Decorator
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------
# Role Required Decorator
# Supports single role or multiple roles
# -----------------------------
def role_required(roles):
    if isinstance(roles, str):
        roles_list = [roles]
    else:
        roles_list = roles

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session or session["role"] not in roles_list:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
