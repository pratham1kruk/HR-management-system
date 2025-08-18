import os

class Config:
    ENV = os.getenv("FLASK_ENV", "development")

    if ENV == "production":  # Railway
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
        MONGO_URI = os.getenv("MONGO_URI")
    else:  # Local Docker Compose
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{os.getenv('POSTGRES_USER', 'hradmin')}:{os.getenv('POSTGRES_PASSWORD', 'secret123')}"
            f"@postgres:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'hrdb')}"
        )
        MONGO_URI = (
            f"mongodb://{os.getenv('MONGO_USER', 'root')}:{os.getenv('MONGO_PASSWORD', 'example')}"
            f"@mongo:{os.getenv('MONGO_PORT', '27017')}/{os.getenv('MONGO_DBNAME', 'hrmongo')}?authSource=admin"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
