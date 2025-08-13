from models.postgres_models import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # Editor or Viewer
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    job_title = db.Column(db.String(100))
    work_phone = db.Column(db.String(20))
    company_name = db.Column(db.String(100))
    country = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ---------- Password handling ----------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---------- Role checks ----------
    def is_editor(self):
        return self.role.lower() == "editor"

    def is_viewer(self):
        return self.role.lower() == "viewer"
