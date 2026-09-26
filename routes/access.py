from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from config import Config
from extensions import db
from models.user import User


def admin_required(view):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        user = db.session.get(User, int(get_jwt_identity()))
        if not user or user.email not in Config.ADMIN_EMAILS:
            return {"error": "admin access required"}, 403
        return view(*args, **kwargs)

    return wrapped


def user_required(view):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return {"error": "user account not found"}, 401
        if user.email in Config.ADMIN_EMAILS:
            return {"error": "user access required"}, 403
        return view(*args, **kwargs)

    return wrapped