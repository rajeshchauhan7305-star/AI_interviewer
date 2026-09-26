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

def _fallback_questions(job_role, count, technology=None):
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

    if technology:
        skill_question = f"How would you use {technology} to solve a practical problem in a {job_role} role?"
        questions = [skill_question] + questions

    return questions[:count]

def generate_questions(job_role, difficulty, count, experience_level="intermediate", technology=None):
    api_key = Config.OPENAI_API_KEY

    if not api_key:
        return _fallback_questions(job_role, count, technology)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""
Generate exactly {count} interview questions for the job role "{job_role}".
Candidate experience level: {experience_level}.
Technology or skill focus: {technology or "general role knowledge"}.
Difficulty: {difficulty} (expert is the highest level).
Return ONLY a JSON array of strings.
Questions should be professional, varied, and suitable for a mock interview. Match the depth to the experience level and include the selected technology where relevant.
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

    return _fallback_questions(job_role, count, technology)


def _extract_json(text):
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _adaptive_follow_up(question, job_role, technology, score):
    focus = f" using {technology}" if technology else ""
    if score >= 80:
        return f"What trade-offs would you consider when applying that approach{focus} at a larger scale?"
    if score < 50:
        return f"Could you explain the core idea behind your answer{focus} with a simple example?"
    return f"Can you walk me through a concrete example of applying that idea{focus} in a {job_role} project?"


def _fallback_analysis(answer, question="", job_role="your target role", technology=None):
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

    clarity_score = min(100, score + (5 if words >= 25 else 0))
    completeness_score = min(100, score + (10 if words >= 45 else 0))
    return {
        "technical_score": score,
        "accuracy_score": score,
        "communication_score": min(score + 3, 100),
        "relevance_score": min(score + 5, 100),
        "confidence_score": min(score, 100),
        "clarity_score": clarity_score,
        "completeness_score": completeness_score,
        "overall_score": score,
        "strengths": ["You attempted the question clearly."],
        "weaknesses": ["The answer can include more specific examples."],
        "suggestions": ["Use a simple structure: concept, explanation, example."],
        "feedback": feedback,
        "suggested_answer": f"A stronger answer would explain the key idea in the question, then give a specific example relevant to {job_role}.",
        "follow_up_question": _adaptive_follow_up(question, job_role, technology, score)
    }


def _normalize_analysis(result, answer, question, job_role, technology):
    fallback = _fallback_analysis(answer, question, job_role, technology)
    normalized = {}
    for key in (
        "technical_score", "accuracy_score", "communication_score",
        "relevance_score", "confidence_score", "clarity_score",
        "completeness_score", "overall_score",
    ):
        try:
            normalized[key] = max(0, min(100, float(result.get(key, fallback[key]))))
        except (TypeError, ValueError):
            normalized[key] = fallback[key]

    for key in ("strengths", "weaknesses", "suggestions"):
        value = result.get(key, fallback[key])
        normalized[key] = [str(item)[:500] for item in value[:8]] if isinstance(value, list) else fallback[key]

    for key in ("feedback", "suggested_answer", "follow_up_question"):
        value = result.get(key)
        normalized[key] = str(value).strip()[:2000] if value else fallback[key]
    return normalized


def analyze_answer(question, answer, job_role, technology=None, experience_level="intermediate", difficulty="medium"):
    answer = (answer or "").strip()

    if not answer:
        return _fallback_analysis(answer, question, job_role, technology)

    if not Config.OPENAI_API_KEY:
        return _fallback_analysis(answer, question, job_role, technology)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        prompt = f"""
You are an interview evaluator.

Job role: {job_role}
Candidate experience level: {experience_level}
Technology or skill focus: {technology or "general role knowledge"}
Question difficulty: {difficulty}
Question: {question}
Candidate answer: {answer}

Evaluate the candidate fairly. Do not reveal private reasoning. Return ONLY concise feedback as valid JSON with these keys:
technical_score (0-100 number),
accuracy_score (0-100 number),
communication_score (0-100 number),
relevance_score (0-100 number),
confidence_score (0-100 number),
clarity_score (0-100 number),
completeness_score (0-100 number),
overall_score (0-100 number),
strengths (array of strings),
weaknesses (array of strings),
suggestions (array of strings),
feedback (one concise explanation),
suggested_answer (a concise example answer, without inventing candidate experience),
follow_up_question (one question adapted to this answer: strong answers get a deeper question, weak answers get a simpler concept clarification, other answers get a focused example request).
"""

        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=prompt
        )

        result = _extract_json(response.output_text)
        if result:
            return _normalize_analysis(result, answer, question, job_role, technology)

    except Exception:
        pass

    return _fallback_analysis(answer, question, job_role, technology)
