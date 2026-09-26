from secrets import compare_digest

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, limiter
from models.user import User
from config import Config

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
@limiter.limit("5 per hour")
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return {"error": "name, email and password are required"}, 400

    if len(password) < 6:
        return {"error": "password must contain at least 6 characters"}, 400

    if email in Config.ADMIN_EMAILS:
        return {"error": "admin account cannot be registered here"}, 403

    if User.query.filter_by(email=email).first():
        return {"error": "email already registered"}, 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    return {
        "message": "registration successful",
        "email": user.email
    }, 201


@auth_bp.post("/admin-login")
@limiter.limit("5 per minute")
def admin_login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if (
        not Config.ADMIN_EMAIL
        or email != Config.ADMIN_EMAIL
        or not Config.ADMIN_PASSWORD
        or not compare_digest(password, Config.ADMIN_PASSWORD)
    ):
        return {"error": "invalid admin credentials"}, 401

    user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not user:
        return {"error": "admin account is not configured"}, 503

    token = create_access_token(identity=str(user.id))

    return {
        "message": "admin login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": True
        }
    }


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if email in Config.ADMIN_EMAILS:
        return {"error": "use the admin login page"}, 403

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "invalid email or password"}, 401

    token = create_access_token(identity=str(user.id))

    return {
        "message": "login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_admin": user.email in Config.ADMIN_EMAILS
        }
    }


def ensure_admin_account():
    if not Config.ADMIN_EMAIL or not Config.ADMIN_PASSWORD:
        return

    user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    password_hash = generate_password_hash(Config.ADMIN_PASSWORD)

    if user:
        user.password_hash = password_hash
    else:
        db.session.add(User(
            name="Administrator",
            email=Config.ADMIN_EMAIL,
            password_hash=password_hash
        ))

    db.session.commit()
