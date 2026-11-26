import csv
import io
import os
import unittest
from datetime import datetime, timezone


os.environ.update({
    "DATABASE_URL": "sqlite:///:memory:",
    "ADMIN_EMAIL": "admin@example.test",
    "ADMIN_EMAILS": "admin@example.test",
    "ADMIN_PASSWORD": "admin-test-password",
    "OPENAI_API_KEY": "",
    "SECRET_KEY": "admin-test-secret-key-with-at-least-32-characters",
    "JWT_SECRET_KEY": "admin-test-jwt-secret-key-with-at-least-32-characters",
})

from app import create_app
from config import Config
from extensions import db
from models.interview import Interview
from models.user import User
from routes.auth import ensure_admin_account
from werkzeug.security import generate_password_hash


class AdminFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_admin_config = (
            Config.ADMIN_EMAIL,
            Config.ADMIN_EMAILS,
            Config.ADMIN_PASSWORD,
        )
        Config.ADMIN_EMAIL = "admin@example.test"
        Config.ADMIN_EMAILS = {"admin@example.test"}
        Config.ADMIN_PASSWORD = "admin-test-password"
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    @classmethod
    def tearDownClass(cls):
        (
            Config.ADMIN_EMAIL,
            Config.ADMIN_EMAILS,
            Config.ADMIN_PASSWORD,
        ) = cls.original_admin_config

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            ensure_admin_account()
            user = User(
                name="Example Candidate",
                email="candidate@example.test",
                password_hash=generate_password_hash("candidate-password"),
            )
            db.session.add(user)
            db.session.flush()
            db.session.add(Interview(
                user_id=user.id,
                job_role="Python Developer",
                status="completed",
                overall_score=82,
                created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            ))
            db.session.commit()

        self.client = self.app.test_client()
        response = self.client.post("/api/auth/admin-login", json={
            "email": "admin@example.test",
            "password": "admin-test-password",
        })
        self.assertEqual(response.status_code, 200)
        self.headers = {"Authorization": f"Bearer {response.get_json()['token']}"}

    def test_overview_includes_searchable_user_status_and_interview_details(self):
        response = self.client.get("/api/admin/overview", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        candidate = next(user for user in data["users"] if user["email"] == "candidate@example.test")
        self.assertTrue(candidate["is_active"])
        interview = data["interviews"][0]
        self.assertEqual(interview["job_role"], "Python Developer")
        self.assertEqual(interview["difficulty"], "medium")
        self.assertEqual(data["role_performance"][0]["interviews"], 1)

    def test_suspend_blocks_login_and_can_be_reversed(self):
        with self.app.app_context():
            user = User.query.filter_by(email="candidate@example.test").first()
            user_id = user.id

        response = self.client.patch(
            f"/api/admin/users/{user_id}/status",
            headers=self.headers,
            json={"is_active": False},
        )
        self.assertEqual(response.status_code, 200)
        login = self.client.post("/api/auth/login", json={
            "email": "candidate@example.test",
            "password": "candidate-password",
        })
        self.assertEqual(login.status_code, 403)

        response = self.client.patch(
            f"/api/admin/users/{user_id}/status",
            headers=self.headers,
            json={"is_active": True},
        )
        self.assertEqual(response.status_code, 200)
        login = self.client.post("/api/auth/login", json={
            "email": "candidate@example.test",
            "password": "candidate-password",
        })
        self.assertEqual(login.status_code, 200)

    def test_csv_exports_contain_expected_headers(self):
        users = self.client.get("/api/admin/export.csv?type=users", headers=self.headers)
        self.assertEqual(users.status_code, 200)
        self.assertEqual(next(csv.reader(io.StringIO(users.text)))[0:4], [
            "id", "name", "email", "status",
        ])

        interviews = self.client.get("/api/admin/export.csv?type=interviews", headers=self.headers)
        self.assertEqual(interviews.status_code, 200)
        self.assertIn("Python Developer", interviews.text)

    def test_delete_admin_and_invalid_export_are_rejected(self):
        with self.app.app_context():
            admin_id = User.query.filter_by(email="admin@example.test").first().id
        response = self.client.delete(f"/api/admin/users/{admin_id}", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        response = self.client.get("/api/admin/export.csv?type=unknown", headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_bulk_actions_update_users_and_reject_admin_accounts(self):
        with self.app.app_context():
            candidate_id = User.query.filter_by(email="candidate@example.test").first().id
            admin_id = User.query.filter_by(email="admin@example.test").first().id

        response = self.client.patch(
            "/api/admin/users/bulk",
            headers=self.headers,
            json={"ids": [candidate_id], "action": "suspend"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["updated"], 1)

        response = self.client.patch(
            "/api/admin/users/bulk",
            headers=self.headers,
            json={"ids": [candidate_id, admin_id], "action": "delete"},
        )
        self.assertEqual(response.status_code, 400)
        with self.app.app_context():
            candidate = db.session.get(User, candidate_id)
            self.assertIsNotNone(candidate)
            self.assertFalse(candidate.is_active)

        response = self.client.patch(
            "/api/admin/users/bulk",
            headers=self.headers,
            json={"ids": [candidate_id], "action": "delete"},
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(User, candidate_id))


if __name__ == "__main__":
    unittest.main()
