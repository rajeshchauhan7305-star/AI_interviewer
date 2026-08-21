from extensions import db

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id"),
        nullable=False
    )
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=True)

    technical_score = db.Column(db.Float, default=0)
    communication_score = db.Column(db.Float, default=0)
    relevance_score = db.Column(db.Float, default=0)
    confidence_score = db.Column(db.Float, default=0)
    overall_score = db.Column(db.Float, default=0)

    strengths = db.Column(db.Text, default="")
    weaknesses = db.Column(db.Text, default="")
    suggestions = db.Column(db.Text, default="")
    feedback = db.Column(db.Text, default="")
