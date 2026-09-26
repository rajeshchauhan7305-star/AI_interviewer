import os
import unittest


os.environ.update({
    "DATABASE_URL": "sqlite:///:memory:",
    "ADMIN_EMAIL": "",
    "ADMIN_EMAILS": "",
    "ADMIN_PASSWORD": "",
    "OPENAI_API_KEY": "",
    "SECRET_KEY": "test-secret-key-with-at-least-32-characters",
    "JWT_SECRET_KEY": "test-jwt-secret-key-with-at-least-32-characters",
})

from app import create_app
from extensions import db


class AdaptiveInterviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    def setUp(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
        self._register_and_login()

    def _register_and_login(self):
        self.client.post("/api/auth/register", json={
            "name": "Adaptive Candidate",
            "email": "adaptive@example.test",
            "password": "testing123",
        })
        response = self.client.post("/api/auth/login", json={
            "email": "adaptive@example.test",
            "password": "testing123",
        })
        self.assertEqual(response.status_code, 200)
        self.headers = {"Authorization": f"Bearer {response.get_json()['token']}"}

    def test_adaptive_question_flow_and_completed_report(self):
        started = self.client.post("/api/interview/start", headers=self.headers, json={
            "job_role": "Python Developer",
            "difficulty": "expert",
            "experience_level": "student",
            "technology": "Python",
            "question_count": 3,
            "adaptive": True,
        })
        self.assertEqual(started.status_code, 201)
        interview_id = started.get_json()["interview_id"]
        self.assertEqual(started.get_json()["difficulty"], "expert")
        self.assertEqual(len(started.get_json()["questions"]), 1)

        state = self.client.get(f"/api/interview/{interview_id}", headers=self.headers).get_json()
        self.assertEqual(state["experience_level"], "student")
        self.assertEqual(state["technology"], "Python")

        first = self.client.post(f"/api/interview/{interview_id}/answer", headers=self.headers, json={
            "question_id": state["questions"][0]["id"],
            "answer": "I am unsure about this concept.",
            "time_taken_seconds": 34,
            "speech_duration_seconds": 60,
            "spoken_word_count": 10,
            "filler_word_count": 2,
        })
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["next_question"]["difficulty"], "hard")
        self.assertNotIn("suggested_answer", first.get_json()["question"])
        self.assertEqual(self.client.get(f"/api/interview/{interview_id}/result", headers=self.headers).status_code, 409)

        state = self.client.get(f"/api/interview/{interview_id}", headers=self.headers).get_json()
        self.assertEqual(self.client.get(f"/api/interview/{interview_id}/report.pdf", headers=self.headers).status_code, 409)
        self.assertEqual(state["questions"][0]["time_taken_seconds"], 34)
        self.assertEqual(state["questions"][0]["words_per_minute"], 10)
        self.assertEqual(state["questions"][0]["filler_word_count"], 2)
        self.assertEqual(len(state["questions"]), 2)
        previous_follow_up_id = state["questions"][1]["id"]
        strong_answer = (
            "I built a Python API, added input validation, unit tests for edge cases, "
            "measured query latency, and used error handling to isolate failures "
            "so the service was more reliable for users."
        )
        voice_analytics = self.client.get("/api/dashboard", headers=self.headers).get_json()["voice_metrics"]
        self.assertEqual(voice_analytics["spoken_words"], 10)
        self.assertEqual(voice_analytics["words_per_minute"], 10)

        revised = self.client.post(f"/api/interview/{interview_id}/answer", headers=self.headers, json={
            "question_id": state["questions"][0]["id"],
            "answer": strong_answer,
        })
        self.assertEqual(revised.status_code, 200)
        self.assertEqual(revised.get_json()["next_question"]["difficulty"], "expert")
        state = self.client.get(f"/api/interview/{interview_id}", headers=self.headers).get_json()
        self.assertEqual(len(state["questions"]), 2)
        self.assertEqual(state["questions"][1]["id"], previous_follow_up_id)
        self.assertIn("trade-offs", state["questions"][1]["question"])

        second = self.client.post(f"/api/interview/{interview_id}/answer", headers=self.headers, json={
            "question_id": state["questions"][1]["id"],
            "answer": strong_answer,
        })
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.get_json()["next_question"]["difficulty"], "expert")

        state = self.client.get(f"/api/interview/{interview_id}", headers=self.headers).get_json()
        third = self.client.post(f"/api/interview/{interview_id}/answer", headers=self.headers, json={
            "question_id": state["questions"][2]["id"],
            "answer": strong_answer,
        })
        self.assertTrue(third.get_json()["complete"])
        finished = self.client.post(f"/api/interview/{interview_id}/finish", headers=self.headers)
        self.assertEqual(finished.status_code, 200)
        self.assertTrue(any("Achievement unlocked" in item for item in finished.get_json()["notifications"]))

        report = self.client.get(f"/api/interview/{interview_id}/result", headers=self.headers)
        self.assertEqual(report.status_code, 200)
        self.assertEqual(len(report.get_json()["questions"]), 3)
        self.assertTrue(report.get_json()["questions"][0]["suggested_answer"])
        pdf = self.client.get(f"/api/interview/{interview_id}/report.pdf", headers=self.headers)
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf.mimetype, "application/pdf")
        self.assertTrue(pdf.data.startswith(b"%PDF-"))

        dashboard = self.client.get("/api/dashboard", headers=self.headers)
        self.assertEqual(dashboard.status_code, 200)
        analytics = dashboard.get_json()
        self.assertEqual(analytics["completed_interviews"], 1)
        self.assertTrue(analytics["achievements"][0]["unlocked"])
        self.assertEqual(len(analytics["performance_over_time"]), 1)
        self.assertGreater(analytics["category_averages"]["accuracy_score"], 0)
        self.assertTrue(analytics["weak_topics"])

        generated_plan = self.client.post("/api/study-plans/generate", headers=self.headers, json={})
        self.assertEqual(generated_plan.status_code, 201)
        plan = generated_plan.get_json()["plan"]
        self.assertEqual(len(plan["tasks"]), 7)
        self.assertIn("interview feedback", plan["source"].lower())
        updated = self.client.patch(
            f"/api/study-plans/{plan['id']}/tasks/1",
            headers=self.headers,
            json={"completed": True},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["plan"]["completed_tasks"], 1)
        self.assertEqual(updated.get_json()["plan"]["progress_percent"], 14)


if __name__ == "__main__":
    unittest.main()