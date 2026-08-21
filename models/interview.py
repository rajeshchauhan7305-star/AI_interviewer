from datetime import datetime
from extensions import db

class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_role = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(30), default="medium")
    question_count = db.Column(db.Integer, default=5)
    status = db.Column(db.String(30), default="in_progress")
    overall_score = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    questions = db.relationship(
        "Question",
        backref="interview",
        lazy=True,
        cascade="all, delete-orphan"
    )
