from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load env vars
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load config
app.config.from_pyfile('config.py')

# SQLAlchemy init
db = SQLAlchemy(app)

# PyMongo init
mongo = PyMongo(app)
app.config['MONGO'] = mongo  # So current_app.config['MONGO'] works in mongo_models

# --- Import Blueprints ---
from routes.employee_routes import employee_bp
from routes.mongo_routes import mongo_bp
from routes.analytics_routes import analytics_bp

# Register Blueprints
app.register_blueprint(employee_bp, url_prefix="/employees")
app.register_blueprint(mongo_bp, url_prefix="/mongo")
app.register_blueprint(analytics_bp, url_prefix="/analytics")

# --- Home Route ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
