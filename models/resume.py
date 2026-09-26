from datetime import datetime, timezone

from extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"
    __table_args__ = (
        db.Index("ix_resumes_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(120), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    profile_json = db.Column(db.Text, nullable=False)
    analysis_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    job_descriptions = db.relationship(
        "JobDescription",
        backref="resume",
        lazy=True,
        cascade="all, delete-orphan",
    )


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"
    __table_args__ = (
        db.Index("ix_job_descriptions_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False, default="Job description")
    description_text = db.Column(db.Text, nullable=False)
    match_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))