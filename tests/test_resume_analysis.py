import io
import os
import unittest

from docx import Document


os.environ.update({
    "DATABASE_URL": "sqlite:///:memory:",
    "ADMIN_EMAIL": "",
    "ADMIN_EMAILS": "",
    "ADMIN_PASSWORD": "",
    "OPENAI_API_KEY": "",
    "SECRET_KEY": "resume-test-secret-key-with-at-least-32-chars",
    "JWT_SECRET_KEY": "resume-test-jwt-secret-key-with-at-least-32-chars",
})

from app import create_app
from extensions import db


def make_resume_docx():
    document = Document()
    for line in (
        "Jordan Lee",
        "jordan@example.test | +1 415-555-0142",
        "Skills",
        "Python, SQL, Docker, REST APIs",
        "Experience",
        "Built a Python service and SQL reporting tools for the product team.",
        "Education",
        "BSc Computer Science",
        "Projects",
        "Created a REST API with Docker deployment.",
        "Certifications",
        "AWS Cloud Practitioner",
        "Languages",
        "English",
    ):
        document.add_paragraph(line)
    payload = io.BytesIO()
    document.save(payload)
    return payload.getvalue()


class ResumeAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
        self.headers = self._register_and_login("jordan@example.test")

    def _register_and_login(self, email):
        name = email.split("@")[0]
        self.client.post("/api/auth/register", json={
            "name": name,
            "email": email,
            "password": "testing123",
        })
        response = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "testing123",
        })
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.get_json()['token']}"}

    def test_upload_extracts_profile_and_matches_job_description(self):
        uploaded = self.client.post(
            "/api/resumes/upload",
            headers=self.headers,
            data={"file": (io.BytesIO(make_resume_docx()), "jordan-resume.docx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(uploaded.status_code, 201, uploaded.get_json())
        resume = uploaded.get_json()["resume"]
        self.assertEqual(resume["profile"]["name"], "Jordan Lee")
        self.assertEqual(resume["profile"]["email"], "jordan@example.test")
        self.assertIn("Python", resume["analysis"]["skills_detected"])
        self.assertGreater(resume["analysis"]["resume_score"], 0)

        matched = self.client.post(
            f"/api/resumes/{resume['id']}/match",
            headers=self.headers,
            json={
                "title": "Python Backend Engineer",
                "description": "We need Python, SQL, REST APIs, and Docker experience to build backend services.",
            },
        )
        self.assertEqual(matched.status_code, 201, matched.get_json())
        result = matched.get_json()["match"]["result"]
        self.assertIn("Python", result["matching_skills"])
        self.assertIn("REST APIs", result["matching_skills"])
        self.assertGreater(result["match_percentage"], 0)

        other_user = self._register_and_login("other@example.test")
        hidden_resume = self.client.get(f"/api/resumes/{resume['id']}", headers=other_user)
        self.assertEqual(hidden_resume.status_code, 404)

    def test_upload_rejects_unsupported_file_type(self):
        response = self.client.post(
            "/api/resumes/upload",
            headers=self.headers,
            data={"file": (io.BytesIO(b"not a resume"), "resume.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 415)


if __name__ == "__main__":
    unittest.main()