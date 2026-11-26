import csv
import io

from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.interview import Interview
from models.user import User
from routes.access import admin_required
from config import Config

admin_bp = Blueprint("admin", __name__)

@admin_bp.get("/overview")
@admin_required
def overview():
    users = User.query.order_by(User.created_at.desc()).all()
    interviews = Interview.query.order_by(Interview.created_at.desc()).all()
    completed = [item for item in interviews if item.status == "completed"]
    scores = [item.overall_score for item in completed]
    status_counts = {}
    role_scores = {}
    for interview in interviews:
        status_counts[interview.status] = status_counts.get(interview.status, 0) + 1
        if interview.status == "completed":
            role_scores.setdefault(interview.job_role, []).append(interview.overall_score or 0)

    return {
        "stats": {
            "users": len(users),
            "active_users": sum(user.is_active for user in users),
            "interviews": len(interviews),
            "completed_interviews": len(completed),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        },
        "interview_statuses": status_counts,
        "role_performance": [
            {
                "job_role": role,
                "interviews": len(role_scores[role]),
                "average_score": round(sum(role_scores[role]) / len(role_scores[role]), 2),
            }
            for role in sorted(role_scores)
        ],
        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "interviews": len(user.interviews),
                "is_active": user.is_active,
                "is_admin": user.email in Config.ADMIN_EMAILS,
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
                "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
                "difficulty": interview.difficulty,
                "experience_level": interview.experience_level,
                "technology": interview.technology,
                "question_count": interview.question_count,
                "adaptive": interview.adaptive,
            }
            for interview in interviews
        ],
    }


@admin_bp.get("/export.csv")
@admin_required
def export_csv():
    export_type = request.args.get("type", "users")
    output = io.StringIO(newline="")
    writer = csv.writer(output)

    if export_type == "users":
        writer.writerow(["id", "name", "email", "status", "is_admin", "joined_at", "interviews"])
        users = User.query.order_by(User.created_at.desc()).all()
        for user in users:
            writer.writerow([
                user.id, user.name, user.email,
                "active" if user.is_active else "suspended",
                user.email in Config.ADMIN_EMAILS, user.created_at.isoformat(),
                len(user.interviews),
            ])
        filename = "users.csv"
    elif export_type == "interviews":
        writer.writerow([
            "id", "candidate", "email", "job_role", "status", "score", "difficulty",
            "experience_level", "technology", "question_count", "adaptive", "created_at",
            "completed_at",
        ])
        interviews = Interview.query.order_by(Interview.created_at.desc()).all()
        for interview in interviews:
            writer.writerow([
                interview.id, interview.user.name, interview.user.email, interview.job_role,
                interview.status, interview.overall_score, interview.difficulty,
                interview.experience_level, interview.technology, interview.question_count,
                interview.adaptive, interview.created_at.isoformat(),
                interview.completed_at.isoformat() if interview.completed_at else "",
            ])
        filename = "interviews.csv"
    else:
        return {"error": "type must be users or interviews"}, 400

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return {"error": "you cannot delete your own admin account"}, 400

    user = db.session.get(User, user_id)
    if not user:
        return {"error": "user not found"}, 404
    if user.email in Config.ADMIN_EMAILS:
        return {"error": "admin accounts cannot be deleted here"}, 400

    db.session.delete(user)
    db.session.commit()
    return {"message": "user deleted"}


@admin_bp.patch("/users/<int:user_id>/status")
@admin_required
def update_user_status(user_id):
    data = request.get_json(silent=True) or {}
    is_active = data.get("is_active")
    if not isinstance(is_active, bool):
        return {"error": "is_active must be a boolean"}, 400

    user = db.session.get(User, user_id)
    if not user:
        return {"error": "user not found"}, 404
    if user.email in Config.ADMIN_EMAILS:
        return {"error": "admin accounts cannot be suspended here"}, 400

    user.is_active = is_active
    db.session.commit()
    return {"message": "user status updated", "is_active": user.is_active}


@admin_bp.patch("/users/bulk")
@admin_required
def bulk_update_users():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return {"error": "request body must be an object"}, 400
    user_ids = data.get("ids")
    action = data.get("action")

    if not isinstance(user_ids, list) or not user_ids:
        return {"error": "ids must be a non-empty list"}, 400
    if any(not isinstance(user_id, int) or isinstance(user_id, bool) or user_id < 1 for user_id in user_ids):
        return {"error": "ids must contain positive integers"}, 400
    if not isinstance(action, str) or action not in {"suspend", "reactivate", "delete"}:
        return {"error": "action must be suspend, reactivate or delete"}, 400

    users = User.query.filter(User.id.in_(set(user_ids))).all()
    if len(users) != len(set(user_ids)):
        return {"error": "one or more users were not found"}, 404
    if any(user.email in Config.ADMIN_EMAILS for user in users):
        return {"error": "admin accounts cannot be changed here"}, 400

    if action == "delete":
        for user in users:
            db.session.delete(user)
    else:
        active = action == "reactivate"
        for user in users:
            user.is_active = active

    db.session.commit()
    return {"message": "bulk action completed", "updated": len(users), "action": action}