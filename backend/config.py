import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@postgres:5432/{os.getenv('POSTGRES_DB')}"
    )

    MONGO_URI = (
        f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@mongo:27017/"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
