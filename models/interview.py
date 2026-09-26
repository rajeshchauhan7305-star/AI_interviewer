from datetime import datetime, timezone
from extensions import db

class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(30), default="medium")
    question_count = db.Column(db.Integer, default=5)
    experience_level = db.Column(
        db.String(32), nullable=False, default="intermediate", server_default="intermediate"
    )
    technology = db.Column(db.String(120), nullable=True)
    adaptive = db.Column(db.Boolean, nullable=False, default=False, server_default="0")
    status = db.Column(db.String(30), default="in_progress")
    overall_score = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = db.Column(db.DateTime, nullable=True)

    questions = db.relationship(
        "Question",
        backref="interview",
        lazy=True,
        order_by="Question.sequence_number, Question.id",
        cascade="all, delete-orphan"
    )
