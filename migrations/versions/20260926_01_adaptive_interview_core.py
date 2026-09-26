"""Add adaptive interview context and evaluation fields.

Revision ID: 20260926_01
Revises:
Create Date: 2026-09-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260926_01"
down_revision = None
branch_labels = None
depends_on = None


def _add_missing_columns(table, columns):
    bind = op.get_bind()
    if table not in sa.inspect(bind).get_table_names():
        return
    existing = {column["name"] for column in sa.inspect(bind).get_columns(table)}
    for column in columns:
        if column.name not in existing:
            op.add_column(table, column)


def upgrade():
    _add_missing_columns("interviews", [
        sa.Column("experience_level", sa.String(length=32), nullable=False, server_default="intermediate"),
        sa.Column("technology", sa.String(length=120), nullable=True),
        sa.Column("adaptive", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    ])
    _add_missing_columns("questions", [
        sa.Column("sequence_number", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="medium"),
        sa.Column("is_follow_up", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("accuracy_score", sa.Float(), nullable=True, server_default=sa.text("0")),
        sa.Column("clarity_score", sa.Float(), nullable=True, server_default=sa.text("0")),
        sa.Column("completeness_score", sa.Float(), nullable=True, server_default=sa.text("0")),
        sa.Column("time_taken_seconds", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("suggested_answer", sa.Text(), nullable=True),
        sa.Column("follow_up_question", sa.Text(), nullable=True),
    ])

    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "questions" not in tables:
        return

    bind.execute(sa.text(
        "UPDATE questions SET sequence_number = "
        "(SELECT COUNT(*) FROM questions AS previous "
        "WHERE previous.interview_id = questions.interview_id "
        "AND previous.id <= questions.id) "
        "WHERE sequence_number IS NULL"
    ))

    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("questions")}
    if "ix_questions_interview_sequence" not in indexes:
        op.create_index(
            "ix_questions_interview_sequence",
            "questions",
            ["interview_id", "sequence_number"],
        )


def downgrade():
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if "questions" in tables:
        indexes = {index["name"] for index in sa.inspect(bind).get_indexes("questions")}
        if "ix_questions_interview_sequence" in indexes:
            op.drop_index("ix_questions_interview_sequence", table_name="questions")
        columns = {column["name"] for column in sa.inspect(bind).get_columns("questions")}
        for name in (
            "follow_up_question", "suggested_answer", "time_taken_seconds",
            "completeness_score", "clarity_score", "accuracy_score",
            "is_follow_up", "difficulty", "sequence_number",
        ):
            if name in columns:
                op.drop_column("questions", name)

    if "interviews" in tables:
        columns = {column["name"] for column in sa.inspect(bind).get_columns("interviews")}
        for name in ("adaptive", "technology", "experience_level"):
            if name in columns:
                op.drop_column("interviews", name)