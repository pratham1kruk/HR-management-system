import os  # Standard library for environment variables

class Config:
    # PostgreSQL connection URI (from env or default format)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}"
    )

    # MongoDB connection URI (uses authSource for authentication)
    MONGO_URI = os.getenv(
        "MONGO_URI",
        f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@mongo:27017/{os.getenv('MONGO_DBNAME')}?authSource=admin"
    )

    # Disable SQLAlchemy event system for performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask environment (development/production)
    ENV = os.getenv("FLASK_ENV", "development")
    # Secret key for session and security
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
