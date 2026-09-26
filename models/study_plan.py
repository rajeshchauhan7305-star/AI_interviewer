from datetime import datetime, timezone

from extensions import db


class StudyPlan(db.Model):
    __tablename__ = "study_plans"
    __table_args__ = (
        db.Index("ix_study_plans_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    source = db.Column(db.String(200), nullable=False, default="", server_default="")
    tasks_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))