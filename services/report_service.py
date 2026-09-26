import io
import json
import unicodedata
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


SCORE_FIELDS = (
    ("Technical knowledge", "technical_score"),
    ("Accuracy", "accuracy_score"),
    ("Relevance", "relevance_score"),
    ("Communication", "communication_score"),
    ("Confidence", "confidence_score"),
    ("Clarity", "clarity_score"),
    ("Completeness", "completeness_score"),
)


def _safe_text(value):
    ascii_text = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = ascii_text.encode("ascii", "replace").decode("ascii")
    return escape(ascii_text).replace("\n", "<br/>")


def _unique_feedback(questions, field):
    collected = []
    for question in questions:
        try:
            values = json.loads(getattr(question, field) or "[]")
        except (TypeError, json.JSONDecodeError):
            values = []
        if isinstance(values, list):
            collected.extend(str(value) for value in values)
    return list(dict.fromkeys(collected))


def _footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d9ded6"))
    canvas.line(0.65 * inch, 0.55 * inch, 7.85 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#687086"))
    canvas.drawString(0.65 * inch, 0.38 * inch, "AI Interviewer | Private candidate report")
    canvas.drawRightString(7.85 * inch, 0.38 * inch, f"Page {document.page}")
    canvas.restoreState()


def build_interview_report(user, interview):
    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.78 * inch,
        title=f"Interview report - {interview.job_role}",
        author="AI Interviewer",
    )
    sample = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=sample["Title"], fontName="Helvetica-Bold",
        fontSize=21, leading=25, alignment=TA_LEFT,
        textColor=colors.HexColor("#1c2925"), spaceAfter=5,
    )
    sub_style = ParagraphStyle(
        "ReportSub", parent=sample["Normal"], fontSize=9, leading=13,
        textColor=colors.HexColor("#687086"), spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "ReportHeading", parent=sample["Heading2"], fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=colors.HexColor("#314638"),
        spaceBefore=15, spaceAfter=7,
    )
    body_style = ParagraphStyle(
        "ReportBody", parent=sample["BodyText"], fontSize=8.5, leading=12,
        textColor=colors.HexColor("#303a33"), spaceAfter=5,
    )
    small_style = ParagraphStyle(
        "ReportSmall", parent=body_style, fontSize=7.5, leading=10,
        textColor=colors.HexColor("#687086"),
    )
    centered_style = ParagraphStyle("ReportCenter", parent=body_style, alignment=TA_CENTER)

    questions = interview.questions
    story = [
        Paragraph("AI Interviewer | Performance Report", title_style),
        Paragraph(
            f"{_safe_text(interview.job_role)} · {_safe_text(interview.difficulty.title())} difficulty · "
            f"Completed {(interview.completed_at or interview.created_at).strftime('%B %d, %Y')}",
            sub_style,
        ),
    ]

    candidate_data = [
        [Paragraph("CANDIDATE", small_style), Paragraph("INTERVIEW CONFIGURATION", small_style)],
        [
            Paragraph(f"<b>{_safe_text(user.name)}</b><br/>{_safe_text(user.email)}", body_style),
            Paragraph(
                f"Experience: {_safe_text(interview.experience_level)}<br/>"
                f"Technology: {_safe_text(interview.technology or 'General')}<br/>"
                f"Mode: {'Adaptive' if interview.adaptive else 'Standard'}",
                body_style,
            ),
        ],
    ]
    candidate_table = Table(candidate_data, colWidths=[3.55 * inch, 3.15 * inch])
    candidate_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf1e9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9ded6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d9ded6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([candidate_table, Paragraph("Score summary", heading_style)])

    score_rows = [[Paragraph("OVERALL", small_style), Paragraph("SCORE", small_style)]]
    score_rows.append([
        Paragraph("Interview score", body_style),
        Paragraph(f"<b>{round(interview.overall_score or 0)} / 100</b>", centered_style),
    ])
    for label, field in SCORE_FIELDS:
        values = [float(getattr(question, field) or 0) for question in questions if question.answer_text]
        average = round(sum(values) / len(values)) if values else 0
        score_rows.append([Paragraph(_safe_text(label), body_style), Paragraph(f"{average} / 100", centered_style)])
    score_table = Table(score_rows, colWidths=[5.5 * inch, 1.2 * inch], repeatRows=1)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf1e9")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f7f8f5")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9ded6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e2e6df")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(score_table)

    for title, field in (("Strengths", "strengths"), ("Areas to improve", "weaknesses"), ("Preparation suggestions", "suggestions")):
        items = _unique_feedback(questions, field)
        story.append(Paragraph(title, heading_style))
        if items:
            story.append(Paragraph("<br/>".join(f"• {_safe_text(item)}" for item in items[:10]), body_style))
        else:
            story.append(Paragraph("No feedback available.", body_style))

    story.append(Paragraph("Question-by-question evaluation", heading_style))
    for index, question in enumerate(questions, start=1):
        story.append(Paragraph(f"Question {index} · {_safe_text(question.difficulty.title())}", heading_style))
        story.append(Paragraph(f"<b>Prompt:</b> {_safe_text(question.question_text)}", body_style))
        story.append(Paragraph(f"<b>Candidate answer:</b> {_safe_text(question.answer_text or 'No answer')[:6000]}", body_style))
        story.append(Paragraph(f"<b>Evaluation ({round(question.overall_score or 0)}/100):</b> {_safe_text(question.feedback)}", body_style))
        if question.suggested_answer:
            story.append(Paragraph(f"<b>Suggested answer:</b> {_safe_text(question.suggested_answer)}", body_style))
        story.append(Paragraph(f"Response time: {round(question.time_taken_seconds or 0)} seconds", small_style))
        if question.spoken_word_count:
            story.append(Paragraph(
                f"Voice: {question.spoken_word_count} recognized words · "
                f"{round(question.words_per_minute or 0)} WPM · "
                f"{question.filler_word_count} filler words",
                small_style,
            ))
        story.append(Spacer(1, 5))

    story.extend([
        Paragraph("Preparation summary", heading_style),
        Paragraph(
            "Review the improvement suggestions above, practice the concepts that scored lowest, "
            "and repeat a role-focused mock interview to measure progress.",
            body_style,
        ),
    ])
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output.getvalue()