import json

from models.resume import Resume
from services.analytics_service import dashboard_analytics


RESOURCE_LINKS = {
    "python": "https://docs.python.org/3/tutorial/",
    "sql": "https://www.postgresql.org/docs/current/tutorial.html",
    "git": "https://git-scm.com/book/en/v2",
    "react": "https://react.dev/learn",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
    "typescript": "https://www.typescriptlang.org/docs/",
    "docker": "https://docs.docker.com/get-started/",
    "machine learning": "https://scikit-learn.org/stable/user_guide.html",
}

DEFAULT_TOPICS = [
    "Core concepts for your target role",
    "Answer structure and concrete examples",
    "Technical problem-solving",
    "Communication and clarity",
    "Practice a role-focused mock interview",
    "Review previous interview feedback",
    "Prepare concise project explanations",
]


def _topic_resource(topic):
    normalized = topic.lower()
    for skill, url in RESOURCE_LINKS.items():
        if skill in normalized:
            return url
    return None


def generate_study_plan(user_id, title=None):
    analytics = dashboard_analytics(user_id)
    topics = []

    for item in analytics["weak_topics"]:
        topics.append(item["topic"])

    latest_resume = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).first()
    if latest_resume:
        try:
            analysis = json.loads(latest_resume.analysis_json)
        except (TypeError, json.JSONDecodeError):
            analysis = {}
        topics.extend(analysis.get("missing_skills", []))

    selected = list(dict.fromkeys(str(topic).strip() for topic in topics if str(topic).strip()))[:7]
    for topic in DEFAULT_TOPICS:
        if len(selected) >= 7:
            break
        if topic not in selected:
            selected.append(topic)

    tasks = [
        {
            "day": index,
            "topic": topic,
            "objective": f"Spend 30 minutes reviewing {topic.lower()}, then write one short example from your own work or coursework.",
            "resource_url": _topic_resource(topic),
            "completed": False,
        }
        for index, topic in enumerate(selected, start=1)
    ]
    if analytics["completed_interviews"] and latest_resume:
        source = "Interview feedback and resume gaps"
    elif analytics["completed_interviews"]:
        source = "Latest interview feedback"
    elif latest_resume:
        source = "Resume skill gaps"
    else:
        source = "Starter plan; personalize it with an interview or resume analysis"
    return {
        "title": (title or "Your interview preparation plan").strip()[:160],
        "tasks": tasks,
        "source": source,
    }