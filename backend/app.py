from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Flask App Init
app = Flask(__name__)
CORS(app)

# Load config from config.py
from config import Config
app.config.from_object(Config)

# --- Fix: Import db from postgres_models ---
from models.postgres_models import db  # ✅ this uses the same db instance
db.init_app(app)  # ✅ this binds the db with your Flask app

# Initialize MongoDB
app.config["MONGO_URI"] = Config.MONGO_URI
mongo = PyMongo(app)

# Import and Register Blueprints
from routes.employee_routes import employee_bp
from routes.mongo_routes import mongo_bp
from routes.analytics_routes import analytics_bp

app.register_blueprint(employee_bp, url_prefix="/employees")
app.register_blueprint(mongo_bp, url_prefix="/personnel")
app.register_blueprint(analytics_bp, url_prefix="/analytics")

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Run App
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
