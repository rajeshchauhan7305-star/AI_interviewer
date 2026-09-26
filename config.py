import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip()
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    admin_emails = []
    for email in f"{os.getenv('ADMIN_EMAILS', '')},{ADMIN_EMAIL}".split(","):
        value = email.strip().lower()
        if value and value not in admin_emails:
            admin_emails.append(value)
    ADMIN_EMAILS = set(admin_emails)

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'database.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
