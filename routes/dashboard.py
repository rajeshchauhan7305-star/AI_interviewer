from flask import Blueprint
from flask_jwt_extended import get_jwt_identity
from routes.access import user_required
from services.analytics_service import dashboard_analytics

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.get("")
@user_required
def dashboard():
    user_id = int(get_jwt_identity())
    return dashboard_analytics(user_id)
