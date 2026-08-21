import json
import os
import re

from config import Config

ROLE_QUESTIONS = {
    "software developer": [
        "What is object-oriented programming and what are its main principles?",
        "Explain the difference between a process and a thread.",
        "What is a REST API and how does it work?",
        "What is database normalization and why is it useful?",
        "Explain time complexity with an example."
    ],
    "python developer": [
        "What are Python decorators and when would you use them?",
        "Explain the difference between a list, tuple and set in Python.",
        "What is exception handling in Python?",
        "Explain Python virtual environments and why they are useful.",
        "What is the difference between shallow copy and deep copy?"
    ],
    "data analyst": [
        "What is the difference between mean, median and mode?",
        "How would you handle missing values in a dataset?",
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain correlation versus causation.",
        "What is data visualization and why is it important?"
    ],
    "cyber security": [
        "What is the CIA triad in cybersecurity?",
        "What is phishing and how can organizations reduce the risk?",
        "Explain authentication versus authorization.",
        "What is a firewall?",
        "What is hashing and how is it different from encryption?"
    ]
}

def _fallback_questions(job_role, count):
    key = job_role.strip().lower()
    questions = ROLE_QUESTIONS.get(key)

    if not questions:
        questions = [
            f"Tell me about your knowledge of {job_role}.",
            "Describe a technical project you have worked on.",
            "How do you troubleshoot a difficult technical problem?",
            "Explain one important concept related to your target role.",
            "Why should a company hire you for this role?"
        ]

    return questions[:count]

def generate_questions(job_role, difficulty, count):
    api_key = Config.OPENAI_API_KEY

    if not api_key:
        return _fallback_questions(job_role, count)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
Generate exactly {count} interview questions for the job role "{job_role}".
Difficulty: {difficulty}.
Return ONLY a JSON array of strings.
Questions should be professional, varied, and suitable for a mock interview.
"""

        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=prompt
        )

        text = response.output_text.strip()
        data = json.loads(text)

        if isinstance(data, list) and data:
            return [str(x) for x in data[:count]]

    except Exception:
        pass

    return _fallback_questions(job_role, count)


def _extract_json(text):
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _fallback_analysis(answer):
    words = len(answer.split())

    if words == 0:
        score = 0
        feedback = "No answer was provided."
    elif words < 10:
        score = 45
        feedback = "The answer is too short. Add explanation and an example."
    elif words < 25:
        score = 65
        feedback = "The answer is relevant but could use more technical detail."
    else:
        score = 80
        feedback = "The answer provides reasonable detail. Add a concrete example where possible."

    return {
        "technical_score": score,
        "communication_score": min(score + 3, 100),
        "relevance_score": min(score + 5, 100),
        "confidence_score": min(score, 100),
        "overall_score": score,
        "strengths": ["You attempted the question clearly."],
        "weaknesses": ["The answer can include more specific examples."],
        "suggestions": ["Use a simple structure: concept, explanation, example."],
        "feedback": feedback
    }


def analyze_answer(question, answer, job_role):
    answer = (answer or "").strip()

    if not answer:
        return _fallback_analysis(answer)

    if not Config.OPENAI_API_KEY:
        return _fallback_analysis(answer)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        prompt = f"""
You are an interview evaluator.

Job role: {job_role}
Question: {question}
Candidate answer: {answer}

Evaluate the candidate fairly. Return ONLY valid JSON with these keys:
technical_score (0-100 number),
communication_score (0-100 number),
relevance_score (0-100 number),
confidence_score (0-100 number),
overall_score (0-100 number),
strengths (array of strings),
weaknesses (array of strings),
suggestions (array of strings),
feedback (string).

Do not invent facts about the candidate.
"""

        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=prompt
        )

        result = _extract_json(response.output_text)

        if result:
            required = [
                "technical_score", "communication_score",
                "relevance_score", "confidence_score",
                "overall_score", "strengths",
                "weaknesses", "suggestions", "feedback"
            ]

            if all(key in result for key in required):
                return result

    except Exception:
        pass

    return _fallback_analysis(answer)
