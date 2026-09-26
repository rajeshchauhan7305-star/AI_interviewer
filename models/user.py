from datetime import datetime, timezone
from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    interviews = db.relationship(
        "Interview",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    resumes = db.relationship(
        "Resume",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    job_descriptions = db.relationship(
        "JobDescription",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    study_plans = db.relationship(
        "StudyPlan",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
