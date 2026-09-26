import json
import re
from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, request
from flask_jwt_extended import get_jwt_identity

from extensions import db
from models.interview import Interview
from models.question import Question
from models.user import User
from routes.access import user_required
from services.ai_service import generate_questions, analyze_answer
from services.report_service import build_interview_report

interview_bp = Blueprint("interview", __name__)

def current_user_id():
    return int(get_jwt_identity())

def question_to_dict(q, include_suggested_answer=False):
    result = {
        "id": q.id,
        "question": q.question_text,
        "answer": q.answer_text,
        "sequence_number": q.sequence_number,
        "difficulty": q.difficulty,
        "is_follow_up": q.is_follow_up,
        "technical_score": q.technical_score,
        "accuracy_score": q.accuracy_score,
        "communication_score": q.communication_score,
        "relevance_score": q.relevance_score,
        "confidence_score": q.confidence_score,
        "clarity_score": q.clarity_score,
        "completeness_score": q.completeness_score,
        "overall_score": q.overall_score,
        "time_taken_seconds": q.time_taken_seconds,
        "speech_duration_seconds": q.speech_duration_seconds,
        "spoken_word_count": q.spoken_word_count,
        "filler_word_count": q.filler_word_count,
        "words_per_minute": q.words_per_minute,
        "strengths": json.loads(q.strengths or "[]"),
        "weaknesses": json.loads(q.weaknesses or "[]"),
        "suggestions": json.loads(q.suggestions or "[]"),
        "feedback": q.feedback,
        "follow_up_question": q.follow_up_question,
    }
    if include_suggested_answer:
        result["suggested_answer"] = q.suggested_answer
    return result


def _next_difficulty(difficulty, score):
    levels = ["easy", "medium", "hard", "expert"]
    current = levels.index(difficulty) if difficulty in levels else 1
    if score >= 80:
        current = min(current + 1, len(levels) - 1)
    elif score < 50:
        current = max(current - 1, 0)
    return levels[current]

@interview_bp.post("/start")
@user_required
def start_interview():
    data = request.get_json(silent=True) or {}

    job_role = str(data.get("job_role", "")).strip()
    difficulty = str(data.get("difficulty", "medium")).strip().lower()
    experience_level = str(data.get("experience_level", "intermediate")).strip().lower()
    technology = str(data.get("technology", "")).strip()
    count = data.get("question_count", 5)
    adaptive = data.get("adaptive", False)

    if not job_role:
        return {"error": "job_role is required"}, 400
    if len(job_role) > 120 or len(technology) > 120:
        return {"error": "job_role and technology must be 120 characters or fewer"}, 400
    if difficulty not in {"easy", "medium", "hard", "expert"}:
        return {"error": "difficulty must be easy, medium, hard, or expert"}, 400
    if experience_level not in {"student", "entry", "junior", "intermediate", "senior"}:
        return {"error": "experience_level must be student, entry, junior, intermediate, or senior"}, 400
    if not isinstance(adaptive, bool):
        return {"error": "adaptive must be a boolean"}, 400

    try:
        count = max(1, min(int(count), 15))
    except (TypeError, ValueError):
        count = 5

    if difficulty not in {"easy", "medium", "hard", "expert"}:
        difficulty = "medium"

    interview = Interview(
        user_id=current_user_id(),
        job_role=job_role,
        difficulty=difficulty,
        question_count=count,
        experience_level=experience_level,
        technology=technology or None,
        adaptive=adaptive,
    )
    db.session.add(interview)
    db.session.flush()

    requested_questions = 1 if adaptive else count
    questions = generate_questions(
        job_role,
        difficulty,
        requested_questions,
        experience_level=experience_level,
        technology=technology or None,
    )

    for sequence_number, text in enumerate(questions, start=1):
        db.session.add(
            Question(
                interview_id=interview.id,
                question_text=text,
                sequence_number=sequence_number,
                difficulty=difficulty,
            )
        )

    db.session.commit()

    return {
        "message": "interview started",
        "interview_id": interview.id,
        "job_role": job_role,
        "difficulty": difficulty,
        "experience_level": experience_level,
        "technology": technology or None,
        "adaptive": adaptive,
        "question_count": count,
        "questions": [
            {"id": q.id, "question": q.question_text, "sequence_number": q.sequence_number}
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
        "experience_level": interview.experience_level,
        "technology": interview.technology,
        "adaptive": interview.adaptive,
        "question_count": interview.question_count,
        "status": interview.status,
        "overall_score": interview.overall_score,
        "answered_questions": sum(bool(question.answer_text) for question in interview.questions),
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
    if len(answer) > 10_000:
        return {"error": "Answers must be 10,000 characters or fewer."}, 413

    question = Question.query.filter_by(
        id=question_id,
        interview_id=interview.id
    ).first()

    if not question:
        return {"error": "question not found"}, 404

    try:
        time_taken = max(0, min(float(data.get("time_taken_seconds", 0)), 3600))
        speech_duration = max(0, min(float(data.get("speech_duration_seconds", 0)), 3600))
        spoken_word_count = max(0, min(int(data.get("spoken_word_count", 0)), 10000))
        filler_word_count = max(0, min(int(data.get("filler_word_count", 0)), spoken_word_count))
    except (TypeError, ValueError):
        return {"error": "Interview timing and voice metrics must be valid numbers."}, 400

    analysis = analyze_answer(
        question.question_text,
        answer,
        interview.job_role,
        technology=interview.technology,
        experience_level=interview.experience_level,
        difficulty=question.difficulty,
    )

    question.answer_text = answer
    question.time_taken_seconds = time_taken
    question.speech_duration_seconds = speech_duration
    question.spoken_word_count = spoken_word_count
    question.filler_word_count = filler_word_count
    question.words_per_minute = round(spoken_word_count / speech_duration * 60, 2) if speech_duration else 0
    question.technical_score = float(analysis["technical_score"])
    question.accuracy_score = float(analysis["accuracy_score"])
    question.communication_score = float(analysis["communication_score"])
    question.relevance_score = float(analysis["relevance_score"])
    question.confidence_score = float(analysis["confidence_score"])
    question.clarity_score = float(analysis["clarity_score"])
    question.completeness_score = float(analysis["completeness_score"])
    question.overall_score = float(analysis["overall_score"])
    question.strengths = json.dumps(analysis["strengths"])
    question.weaknesses = json.dumps(analysis["weaknesses"])
    question.suggestions = json.dumps(analysis["suggestions"])
    question.feedback = str(analysis["feedback"])
    question.suggested_answer = str(analysis["suggested_answer"])
    question.follow_up_question = str(analysis["follow_up_question"])

    next_question = None
    if interview.adaptive:
        Question.query.filter(
            Question.interview_id == interview.id,
            Question.sequence_number > question.sequence_number,
        ).delete(synchronize_session=False)
        db.session.flush()
        db.session.expire(interview, ["questions"])

    if interview.adaptive and len(interview.questions) < interview.question_count:
        next_difficulty = _next_difficulty(question.difficulty, question.overall_score)
        next_question = Question(
            interview_id=interview.id,
            question_text=question.follow_up_question,
            sequence_number=len(interview.questions) + 1,
            difficulty=next_difficulty,
            is_follow_up=True,
        )
        db.session.add(next_question)
        db.session.flush()

    db.session.commit()

    adaptive_complete = interview.adaptive and next_question is None
    return {
        "message": "answer analyzed",
        "question": question_to_dict(question),
        "next_question": {
            "id": next_question.id,
            "question": next_question.question_text,
            "sequence_number": next_question.sequence_number,
            "difficulty": next_question.difficulty,
            "is_follow_up": next_question.is_follow_up,
        } if next_question else None,
        "complete": adaptive_complete,
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

    unanswered = [question for question in interview.questions if not question.answer_text]
    if unanswered or (interview.adaptive and len(interview.questions) < interview.question_count):
        return {"error": "answer all interview questions before finishing"}, 400

    answered = [
        q.overall_score for q in interview.questions
        if q.answer_text
    ]
    previous_interview = Interview.query.filter(
        Interview.user_id == current_user_id(),
        Interview.status == "completed",
        Interview.id != interview.id,
    ).order_by(Interview.completed_at.desc()).first()

    interview.overall_score = round(
        sum(answered) / len(answered), 2
    ) if answered else 0

    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.session.commit()

    notifications = ["Interview completed. Your report is ready."]
    if previous_interview is None:
        notifications.append("Achievement unlocked: First Interview.")
    elif interview.overall_score > float(previous_interview.overall_score or 0):
        notifications.append("Your score improved from the previous interview.")

    return {
        "message": "interview completed",
        "interview_id": interview.id,
        "overall_score": interview.overall_score,
        "answered_questions": len(answered),
        "total_questions": len(interview.questions),
        "notifications": notifications,
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
    if interview.status != "completed":
        return {"error": "interview is not complete"}, 409

    questions = [question_to_dict(q, include_suggested_answer=True) for q in interview.questions]

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
        "experience_level": interview.experience_level,
        "technology": interview.technology,
        "adaptive": interview.adaptive,
        "overall_score": interview.overall_score,
        "strengths": list(dict.fromkeys(all_strengths)),
        "weaknesses": list(dict.fromkeys(all_weaknesses)),
        "suggestions": list(dict.fromkeys(all_suggestions)),
        "questions": questions
    }


@interview_bp.get("/<int:interview_id>/report.pdf")
@user_required
def download_report(interview_id):
    interview = Interview.query.filter_by(
        id=interview_id,
        user_id=current_user_id(),
    ).first()
    if not interview:
        return {"error": "interview not found"}, 404
    if interview.status != "completed":
        return {"error": "interview is not complete"}, 409

    candidate = db.session.get(User, current_user_id())
    if not candidate:
        return {"error": "candidate account not found"}, 404

    try:
        pdf = build_interview_report(candidate, interview)
    except Exception:
        current_app.logger.exception("Interview PDF generation failed")
        return {"error": "The interview report could not be generated."}, 500

    role = re.sub(r"[^a-zA-Z0-9_-]+", "-", interview.job_role).strip("-")[:50] or "interview"
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="interview-{role}-{interview.id}.pdf"'},
    )
