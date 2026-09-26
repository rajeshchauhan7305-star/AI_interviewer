from flask import Blueprint
from flask_jwt_extended import get_jwt_identity
from extensions import db
from models.interview import Interview
from routes.access import user_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.get("")
@user_required
def dashboard():
    user_id = int(get_jwt_identity())

    interviews = Interview.query.filter_by(user_id=user_id).all()
    completed = [i for i in interviews if i.status == "completed"]
    scores = [i.overall_score for i in completed]

    return {
        "total_interviews": len(interviews),
        "completed_interviews": len(completed),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "recent_interviews": [
            {
                "id": i.id,
                "job_role": i.job_role,
                "score": i.overall_score,
                "status": i.status,
                "created_at": i.created_at.isoformat()
            }
            for i in sorted(interviews, key=lambda x: x.created_at, reverse=True)[:5]
        ]
    }
