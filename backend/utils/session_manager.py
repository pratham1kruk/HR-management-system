from flask import session
from models.user import User
from models.postgres_models import db

# -----------------------------
# Get Current Logged-in User
# -----------------------------
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

# -----------------------------
# Clear Session on Logout
# -----------------------------
def clear_session():
    keys_to_clear = ["user_id", "role", "otp", "reset_user_id"]
    for key in keys_to_clear:
        session.pop(key, None)
