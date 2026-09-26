import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-jwt-secret")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
    ADMIN_EMAILS = {
        email.strip().lower()
        for email in f"{os.getenv('ADMIN_EMAILS', '')},{ADMIN_EMAIL}".split(",")
        if email.strip()
    }
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'database.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
