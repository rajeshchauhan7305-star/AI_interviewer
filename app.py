from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import inspect, text
from werkzeug.exceptions import RequestEntityTooLarge
from extensions import db, jwt, limiter, migrate
from routes.auth import auth_bp, ensure_admin_account
from routes.interview import interview_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.resumes import resumes_bp
from routes.study_plans import study_plans_bp
from config import Config


def ensure_database_schema():
    with db.engine.begin() as connection:
        inspector = inspect(connection)
        tables = set(inspector.get_table_names())

        if "interviews" in tables:
            interview_columns = {col["name"] for col in inspector.get_columns("interviews")}
            missing = [
                ("experience_level", "VARCHAR(32)", "NOT NULL DEFAULT 'intermediate'"),
                ("technology", "VARCHAR(120)", "NULL"),
                ("adaptive", "BOOLEAN", "NOT NULL DEFAULT 0"),
            ]
            for column_name, column_type, column_constraints in missing:
                if column_name not in interview_columns:
                    sql = f"ALTER TABLE interviews ADD COLUMN {column_name} {column_type} {column_constraints}"
                    connection.execute(text(sql))

        if "questions" in tables:
            question_columns = {col["name"] for col in inspector.get_columns("questions")}
            missing = [
                ("sequence_number", "INTEGER", "NULL"),
                ("difficulty", "VARCHAR(30)", "NOT NULL DEFAULT 'medium'"),
                ("is_follow_up", "BOOLEAN", "NOT NULL DEFAULT 0"),
                ("accuracy_score", "FLOAT", "DEFAULT 0"),
                ("clarity_score", "FLOAT", "DEFAULT 0"),
                ("completeness_score", "FLOAT", "DEFAULT 0"),
                ("time_taken_seconds", "FLOAT", "NOT NULL DEFAULT 0"),
                ("speech_duration_seconds", "FLOAT", "NOT NULL DEFAULT 0"),
                ("spoken_word_count", "INTEGER", "NOT NULL DEFAULT 0"),
                ("filler_word_count", "INTEGER", "NOT NULL DEFAULT 0"),
                ("words_per_minute", "FLOAT", "NOT NULL DEFAULT 0"),
                ("suggested_answer", "TEXT", "NULL"),
                ("follow_up_question", "TEXT", "NULL"),
            ]
            for column_name, column_type, column_constraints in missing:
                if column_name not in question_columns:
                    sql = f"ALTER TABLE questions ADD COLUMN {column_name} {column_type} {column_constraints}"
                    connection.execute(text(sql))


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(interview_bp, url_prefix="/api/interview")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(resumes_bp, url_prefix="/api/resumes")
    app.register_blueprint(study_plans_bp, url_prefix="/api/study-plans")

    with app.app_context():
        db.create_all()
        ensure_database_schema()
        ensure_admin_account()

    @app.get("/")
    def home():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        return {"error": "Request is too large. Resume files must be 5 MB or smaller."}, 413

    @app.errorhandler(429)
    def too_many_requests(_error):
        return {"error": "Too many requests. Please wait before trying again."}, 429

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
