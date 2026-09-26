import json
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.interview import Interview
from models.question import Question
from routes.access import user_required
from services.ai_service import generate_questions, analyze_answer

interview_bp = Blueprint("interview", __name__)

def current_user_id():
    return int(get_jwt_identity())

def question_to_dict(q):
    return {
        "id": q.id,
        "question": q.question_text,
        "answer": q.answer_text,
        "technical_score": q.technical_score,
        "communication_score": q.communication_score,
        "relevance_score": q.relevance_score,
        "confidence_score": q.confidence_score,
        "overall_score": q.overall_score,
        "strengths": json.loads(q.strengths or "[]"),
        "weaknesses": json.loads(q.weaknesses or "[]"),
        "suggestions": json.loads(q.suggestions or "[]"),
        "feedback": q.feedback
    }

@interview_bp.post("/start")
@user_required
def start_interview():
    data = request.get_json(silent=True) or {}

    job_role = str(data.get("job_role", "")).strip()
    difficulty = str(data.get("difficulty", "medium")).strip().lower()
    count = data.get("question_count", 5)

    if not job_role:
        return {"error": "job_role is required"}, 400

    try:
        count = max(1, min(int(count), 15))
    except (TypeError, ValueError):
        count = 5

    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    interview = Interview(
        user_id=current_user_id(),
        job_role=job_role,
        difficulty=difficulty,
        question_count=count
    )
    db.session.add(interview)
    db.session.flush()

    questions = generate_questions(job_role, difficulty, count)

    for text in questions:
        db.session.add(
            Question(
                interview_id=interview.id,
                question_text=text
            )
        )

    db.session.commit()

    return {
        "message": "interview started",
        "interview_id": interview.id,
        "job_role": job_role,
        "difficulty": difficulty,
        "questions": [
            {"id": q.id, "question": q.question_text}
            for q in interview.questions
        ]
    }, 201


@interview_bp.get("/<int:interview_id>")
@user_required
def get_interview(interview_id):
    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=current_user_id()
    ).first()

    if not interview:
        return {"error": "interview not found"}, 404

    return {
        "id": interview.id,
        "job_role": interview.job_role,
        "difficulty": interview.difficulty,
        "status": interview.status,
        "overall_score": interview.overall_score,
        "questions": [question_to_dict(q) for q in interview.questions]
    }


@interview_bp.post("/<int:interview_id>/answer")
@user_required
def submit_answer(interview_id):
    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=current_user_id()
    ).first()

    if not interview:
        return {"error": "interview not found"}, 404

    if interview.status == "completed":
        return {"error": "interview already completed"}, 400

    data = request.get_json(silent=True) or {}
    question_id = data.get("question_id")
    answer = str(data.get("answer", "")).strip()

    if not question_id or not answer:
        return {"error": "question_id and answer are required"}, 400

    question = Question.query.filter_by(
        id=question_id,
        interview_id=interview.id
    ).first()

    if not question:
        return {"error": "question not found"}, 404

    analysis = analyze_answer(
        question.question_text,
        answer,
        interview.job_role
    )

    question.answer_text = answer
    question.technical_score = float(analysis["technical_score"])
    question.communication_score = float(analysis["communication_score"])
    question.relevance_score = float(analysis["relevance_score"])
    question.confidence_score = float(analysis["confidence_score"])
    question.overall_score = float(analysis["overall_score"])
    question.strengths = json.dumps(analysis["strengths"])
    question.weaknesses = json.dumps(analysis["weaknesses"])
    question.suggestions = json.dumps(analysis["suggestions"])
    question.feedback = str(analysis["feedback"])

    db.session.commit()

    return {
        "message": "answer analyzed",
        "question": question_to_dict(question)
    }


@interview_bp.post("/<int:interview_id>/finish")
@user_required
def finish_interview(interview_id):
    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=current_user_id()
    ).first()

    if not interview:
        return {"error": "interview not found"}, 404

    answered = [
        q.overall_score for q in interview.questions
        if q.answer_text
    ]

    interview.overall_score = round(
        sum(answered) / len(answered), 2
    ) if answered else 0

    interview.status = "completed"
    interview.completed_at = datetime.utcnow()

    db.session.commit()

    return {
        "message": "interview completed",
        "interview_id": interview.id,
        "overall_score": interview.overall_score,
        "answered_questions": len(answered),
        "total_questions": len(interview.questions)
    }


@interview_bp.get("/history/all")
@user_required
def history():
    interviews = Interview.query.filter_by(
        user_id=current_user_id()
    ).order_by(Interview.created_at.desc()).all()

    return {
        "interviews": [
            {
                "id": i.id,
                "job_role": i.job_role,
                "difficulty": i.difficulty,
                "status": i.status,
                "overall_score": i.overall_score,
                "created_at": i.created_at.isoformat()
            }
            for i in interviews
        ]
    }


@interview_bp.get("/<int:interview_id>/result")
@user_required
def result(interview_id):
    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=current_user_id()
    ).first()

    if not interview:
        return {"error": "interview not found"}, 404

    questions = [question_to_dict(q) for q in interview.questions]

    all_strengths = []
    all_weaknesses = []
    all_suggestions = []

    for q in questions:
        all_strengths.extend(q["strengths"])
        all_weaknesses.extend(q["weaknesses"])
        all_suggestions.extend(q["suggestions"])

    return {
        "interview_id": interview.id,
        "job_role": interview.job_role,
        "difficulty": interview.difficulty,
        "overall_score": interview.overall_score,
        "strengths": list(dict.fromkeys(all_strengths)),
        "weaknesses": list(dict.fromkeys(all_weaknesses)),
        "suggestions": list(dict.fromkeys(all_suggestions)),
        "questions": questions
    }
