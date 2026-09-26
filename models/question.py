from extensions import db

class Question(db.Model):
    __tablename__ = "questions"
    __table_args__ = (
        db.Index("ix_questions_interview_sequence", "interview_id", "sequence_number"),
    )

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(
        db.Integer,
        db.ForeignKey("interviews.id"),
        nullable=False
    )
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    sequence_number = db.Column(db.Integer, nullable=True)
    difficulty = db.Column(db.String(30), nullable=False, default="medium", server_default="medium")
    is_follow_up = db.Column(db.Boolean, nullable=False, default=False, server_default="0")

    technical_score = db.Column(db.Float, default=0)
    accuracy_score = db.Column(db.Float, default=0)
    communication_score = db.Column(db.Float, default=0)
    relevance_score = db.Column(db.Float, default=0)
    confidence_score = db.Column(db.Float, default=0)
    clarity_score = db.Column(db.Float, default=0)
    completeness_score = db.Column(db.Float, default=0)
    overall_score = db.Column(db.Float, default=0)
    time_taken_seconds = db.Column(db.Float, nullable=False, default=0, server_default="0")
    speech_duration_seconds = db.Column(db.Float, nullable=False, default=0, server_default="0")
    spoken_word_count = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    filler_word_count = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    words_per_minute = db.Column(db.Float, nullable=False, default=0, server_default="0")

    strengths = db.Column(db.Text, default="")
    weaknesses = db.Column(db.Text, default="")
    suggestions = db.Column(db.Text, default="")
    feedback = db.Column(db.Text, default="")
    suggested_answer = db.Column(db.Text, nullable=True)
    follow_up_question = db.Column(db.Text, nullable=True)
