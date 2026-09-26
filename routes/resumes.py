import json
from pathlib import Path

from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from extensions import db
from models.resume import JobDescription, Resume
from routes.access import user_required
from services.resume_service import (
    MAX_UPLOAD_BYTES,
    ResumeParseError,
    analyze_resume,
    extract_profile,
    extract_resume_text,
    match_job_description,
)


resumes_bp = Blueprint("resumes", __name__)
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_DESCRIPTION_CHARS = 50_000


def _resume_response(resume):
    return {
        "id": resume.id,
        "filename": resume.filename,
        "content_type": resume.content_type,
        "profile": json.loads(resume.profile_json),
        "analysis": json.loads(resume.analysis_json),
        "created_at": resume.created_at.isoformat(),
        "matches": [
            {
                "id": item.id,
                "title": item.title,
                "created_at": item.created_at.isoformat(),
                "result": json.loads(item.match_json),
            }
            for item in sorted(resume.job_descriptions, key=lambda match: match.created_at, reverse=True)
        ],
    }


def _owned_resume(resume_id):
    return Resume.query.filter_by(
        id=resume_id,
        user_id=int(get_jwt_identity()),
    ).first()


@resumes_bp.get("")
@user_required
def list_resumes():
    user_id = int(get_jwt_identity())
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    return {"resumes": [_resume_response(resume) for resume in resumes]}


@resumes_bp.post("/upload")
@user_required
def upload_resume():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return {"error": "Choose a PDF, DOC, or DOCX resume to upload."}, 400

    filename = secure_filename(uploaded.filename)
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in ALLOWED_EXTENSIONS:
        return {"error": "Supported resume formats are PDF, DOC, and DOCX."}, 415

    payload = uploaded.stream.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        return {"error": "Resume files must be 5 MB or smaller."}, 413

    try:
        text = extract_resume_text(filename, payload)
        profile = extract_profile(text)
        analysis = analyze_resume(profile, text)
    except ResumeParseError as error:
        return {"error": str(error)}, 400
    except Exception:
        current_app.logger.exception("Resume analysis failed")
        return {"error": "The resume could not be analyzed. Please try another file."}, 422

    resume = Resume(
        user_id=int(get_jwt_identity()),
        filename=filename,
        content_type=uploaded.mimetype or "application/octet-stream",
        extracted_text=text,
        profile_json=json.dumps(profile),
        analysis_json=json.dumps(analysis),
    )
    db.session.add(resume)
    db.session.commit()
    return {"resume": _resume_response(resume)}, 201


@resumes_bp.get("/<int:resume_id>")
@user_required
def get_resume(resume_id):
    resume = _owned_resume(resume_id)
    if not resume:
        return {"error": "resume not found"}, 404
    return {"resume": _resume_response(resume)}


@resumes_bp.post("/<int:resume_id>/match")
@user_required
def match_resume(resume_id):
    resume = _owned_resume(resume_id)
    if not resume:
        return {"error": "resume not found"}, 404

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "Job description")).strip() or "Job description"
    description = str(data.get("description", "")).strip()
    if len(title) > 120:
        return {"error": "Job title must be 120 characters or fewer."}, 400
    if len(description) < 20:
        return {"error": "Enter a job description with at least 20 characters."}, 400
    if len(description) > MAX_DESCRIPTION_CHARS:
        return {"error": "Job descriptions must be 50,000 characters or fewer."}, 413

    result = match_job_description(
        json.loads(resume.profile_json),
        resume.extracted_text,
        description,
    )
    match = JobDescription(
        user_id=int(get_jwt_identity()),
        resume_id=resume.id,
        title=title,
        description_text=description,
        match_json=json.dumps(result),
    )
    db.session.add(match)
    db.session.commit()
    return {"match": {"id": match.id, "title": match.title, "result": result}}, 201