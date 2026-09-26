import json
from collections import Counter, defaultdict
from datetime import date, timedelta

from models.interview import Interview
from models.question import Question


SCORE_FIELDS = {
    "technical_score": "technical_score",
    "accuracy_score": "accuracy_score",
    "communication_score": "communication_score",
    "relevance_score": "relevance_score",
    "confidence_score": "confidence_score",
    "clarity_score": "clarity_score",
    "completeness_score": "completeness_score",
}


def _mean(values):
    return round(sum(values) / len(values), 2) if values else 0


def _items(value):
    try:
        result = json.loads(value or "[]")
        return result if isinstance(result, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def _interview_streak(interviews):
    days = sorted({item.completed_at.date() for item in interviews if item.completed_at}, reverse=True)
    if not days or days[0] < date.today() - timedelta(days=1):
        return 0
    streak = 0
    expected = days[0]
    for completed_day in days:
        if completed_day != expected:
            break
        streak += 1
        expected -= timedelta(days=1)
    return streak


def dashboard_analytics(user_id):
    interviews = Interview.query.filter_by(user_id=user_id).order_by(Interview.created_at.desc()).all()
    completed = sorted(
        (item for item in interviews if item.status == "completed"),
        key=lambda item: item.completed_at or item.created_at,
        reverse=True,
    )
    questions = Question.query.join(Interview).filter(
        Interview.user_id == user_id,
        Question.answer_text.isnot(None),
    ).all()
    scores = [float(item.overall_score or 0) for item in completed]
    voice_questions = [question for question in questions if question.spoken_word_count]
    total_speech_seconds = sum(float(question.speech_duration_seconds or 0) for question in voice_questions)
    total_spoken_words = sum(int(question.spoken_word_count or 0) for question in voice_questions)
    total_fillers = sum(int(question.filler_word_count or 0) for question in voice_questions)
    category_averages = {
        label: _mean([float(getattr(question, field) or 0) for question in questions])
        for label, field in SCORE_FIELDS.items()
    }

    by_role = defaultdict(list)
    for interview in completed:
        by_role[interview.job_role].append(float(interview.overall_score or 0))
    role_performance = [
        {"job_role": role, "average_score": _mean(values), "interviews": len(values)}
        for role, values in sorted(by_role.items(), key=lambda item: _mean(item[1]), reverse=True)
    ]

    strengths = Counter(item for question in questions for item in _items(question.strengths))
    weaknesses = Counter(item for question in questions for item in _items(question.weaknesses))
    latest_score = scores[0] if scores else None
    previous_score = scores[1] if len(scores) > 1 else None
    improvement = None
    if latest_score is not None and previous_score is not None:
        improvement = round(latest_score - previous_score, 2)

    achievements = [
        {"id": "first-interview", "title": "First Interview", "description": "Complete your first mock interview.", "unlocked": len(completed) >= 1},
        {"id": "interview-regular", "title": "Interview Regular", "description": "Complete 10 mock interviews.", "unlocked": len(completed) >= 10},
        {"id": "week-streak", "title": "7-Day Streak", "description": "Practice on seven consecutive days.", "unlocked": _interview_streak(completed) >= 7},
        {"id": "improvement", "title": "Improvement", "description": "Score higher than your previous interview.", "unlocked": improvement is not None and improvement > 0},
        {"id": "technical-expert", "title": "Technical Expert", "description": "Average at least 85% across three completed interviews.", "unlocked": len(completed) >= 3 and category_averages["technical_score"] >= 85},
    ]

    return {
        "total_interviews": len(interviews),
        "completed_interviews": len(completed),
        "average_score": _mean(scores),
        "best_score": max(scores) if scores else 0,
        "interview_streak": _interview_streak(completed),
        "latest_score": latest_score,
        "previous_score": previous_score,
        "improvement_points": improvement,
        "category_averages": category_averages,
        "voice_metrics": {
            "speaking_seconds": round(total_speech_seconds),
            "spoken_words": total_spoken_words,
            "filler_words": total_fillers,
            "words_per_minute": round(total_spoken_words / total_speech_seconds * 60, 1) if total_speech_seconds else 0,
        },
        "achievements": achievements,
        "role_performance": role_performance,
        "strong_topics": [{"topic": topic, "count": count} for topic, count in strengths.most_common(5)],
        "weak_topics": [{"topic": topic, "count": count} for topic, count in weaknesses.most_common(5)],
        "performance_over_time": [
            {
                "date": (item.completed_at or item.created_at).date().isoformat(),
                "job_role": item.job_role,
                "score": round(float(item.overall_score or 0), 2),
            }
            for item in list(reversed(completed[:8]))
        ],
    }