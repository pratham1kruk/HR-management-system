from flask import Flask, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Initialize Flask App
# -----------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Load config from config.py
from config import Config
app.config.from_object(Config)

# -----------------------------
# Initialize PostgreSQL
# -----------------------------
from models.postgres_models import db
db.init_app(app)

# -----------------------------
# Initialize MongoDB
# -----------------------------
app.config["MONGO_URI"] = Config.MONGO_URI
mongo = PyMongo(app)
# Make mongo accessible app-wide
app.config["MONGO"] = mongo

# -----------------------------
# Register Blueprints
# -----------------------------
from routes.employee_routes import employee_bp
from routes.mongo_routes import mongo_bp
from routes.analytics_routes import analytics_bp
from routes.mongo_analytics_routes import mongo_analytics_bp
from routes.auth_routes import auth_bp

app.register_blueprint(employee_bp, url_prefix="/employees")
app.register_blueprint(mongo_bp, url_prefix="/personnel")
app.register_blueprint(analytics_bp, url_prefix="/analytics")
app.register_blueprint(mongo_analytics_bp, url_prefix="/mongo-analytics")
app.register_blueprint(auth_bp, url_prefix="/auth")

# -----------------------------
# Import decorator for login
# -----------------------------
from utils.decorator import login_required

# -----------------------------
# Home Page (requires login)
# -----------------------------
@app.route("/")
def home():
    # If user is logged in → main page
    if session.get("user_id"):
        return render_template("index.html")
    # If not logged in → landing page
    return redirect(url_for("auth.auth_home"))

# -----------------------------
# Optional: Create tables on first run
# -----------------------------
with app.app_context():
    db.create_all()

# -----------------------------
# Run the Flask App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
