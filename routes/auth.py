from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return {"error": "name, email and password are required"}, 400

    if len(password) < 6:
        return {"error": "password must contain at least 6 characters"}, 400

    if User.query.filter_by(email=email).first():
        return {"error": "email already registered"}, 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return {
        "message": "registration successful",
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }, 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "invalid email or password"}, 401

    token = create_access_token(identity=str(user.id))

    return {
        "message": "login successful",
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }
