from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db, jwt
from routes.auth import auth_bp
from routes.interview import interview_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from config import Config

def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(interview_bp, url_prefix="/api/interview")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
