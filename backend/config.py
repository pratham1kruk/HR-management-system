import os

class Config:
    # PostgreSQL connection URI
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"postgresql://{os.getenv('POSTGRES_USER', 'hradmin')}:{os.getenv('POSTGRES_PASSWORD', 'secret123')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'hrdb')}"
    )

    # MongoDB connection URI
    MONGO_URI = os.getenv(
        "MONGO_URI",
        f"mongodb://{os.getenv('MONGO_USER', 'root')}:{os.getenv('MONGO_PASSWORD', 'example')}@{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', '27017')}/{os.getenv('MONGO_DBNAME', 'hrmongo')}?authSource=admin"
    )

    # Disable SQLAlchemy event system for performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask environment (development/production)
    ENV = os.getenv("FLASK_ENV", "development")

    # Secret key for sessions and security
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
