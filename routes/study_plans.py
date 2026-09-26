import json

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.study_plan import StudyPlan
from routes.access import user_required
from services.study_plan_service import generate_study_plan


study_plans_bp = Blueprint("study_plans", __name__)


def _plan_response(plan):
    tasks = json.loads(plan.tasks_json)
    completed = sum(bool(task.get("completed")) for task in tasks)
    return {
        "id": plan.id,
        "title": plan.title,
        "source": plan.source,
        "created_at": plan.created_at.isoformat(),
        "tasks": tasks,
        "completed_tasks": completed,
        "progress_percent": round(completed / len(tasks) * 100) if tasks else 0,
    }


@study_plans_bp.get("")
@user_required
def list_plans():
    user_id = int(get_jwt_identity())
    plans = StudyPlan.query.filter_by(user_id=user_id).order_by(StudyPlan.created_at.desc()).all()
    return {"plans": [_plan_response(plan) for plan in plans]}


@study_plans_bp.post("/generate")
@user_required
def create_plan():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "Your interview preparation plan")).strip()
    if len(title) > 160:
        return {"error": "Plan title must be 160 characters or fewer."}, 400

    user_id = int(get_jwt_identity())
    generated = generate_study_plan(user_id, title)
    plan = StudyPlan(
        user_id=user_id,
        title=generated["title"],
        source=generated["source"],
        tasks_json=json.dumps(generated["tasks"]),
    )
    db.session.add(plan)
    db.session.commit()
    return {"plan": _plan_response(plan)}, 201


@study_plans_bp.patch("/<int:plan_id>/tasks/<int:day>")
@user_required
def update_task(plan_id, day):
    plan = StudyPlan.query.filter_by(
        id=plan_id,
        user_id=int(get_jwt_identity()),
    ).first()
    if not plan:
        return {"error": "study plan not found"}, 404

    data = request.get_json(silent=True) or {}
    completed = data.get("completed")
    if not isinstance(completed, bool):
        return {"error": "completed must be a boolean"}, 400

    tasks = json.loads(plan.tasks_json)
    task = next((item for item in tasks if item.get("day") == day), None)
    if not task:
        return {"error": "study task not found"}, 404
    task["completed"] = completed
    plan.tasks_json = json.dumps(tasks)
    db.session.commit()
    return {"plan": _plan_response(plan)}