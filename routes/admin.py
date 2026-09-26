from flask import Blueprint
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.interview import Interview
from models.user import User
from routes.access import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/overview")
@admin_required
def overview():
    users = User.query.order_by(User.created_at.desc()).all()
    interviews = Interview.query.order_by(Interview.created_at.desc()).all()
    completed = [item for item in interviews if item.status == "completed"]
    scores = [item.overall_score for item in completed]

    return {
        "stats": {
            "users": len(users),
            "interviews": len(interviews),
            "completed_interviews": len(completed),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        },
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "interviews": len(user.interviews),
            }
            for user in users
        ],
        "interviews": [
            {
                "id": interview.id,
                "candidate": interview.user.name,
                "email": interview.user.email,
                "job_role": interview.job_role,
                "status": interview.status,
                "score": interview.overall_score,
                "created_at": interview.created_at.isoformat(),
            }
            for interview in interviews[:25]
        ],
    }


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return {"error": "you cannot delete your own admin account"}, 400

    user = db.session.get(User, user_id)
    if not user:
        return {"error": "user not found"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "user deleted"}