"""Persist browser speech interview metrics.

Revision ID: 20260926_04
Revises: 20260926_03
Create Date: 2026-09-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260926_04"
down_revision = "20260926_03"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if "questions" not in sa.inspect(bind).get_table_names():
        return
    existing = {item["name"] for item in sa.inspect(bind).get_columns("questions")}
    columns = (
        sa.Column("speech_duration_seconds", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("spoken_word_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("filler_word_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("words_per_minute", sa.Float(), nullable=False, server_default=sa.text("0")),
    )
    for column in columns:
        if column.name not in existing:
            op.add_column("questions", column)


def downgrade():
    bind = op.get_bind()
    if "questions" not in sa.inspect(bind).get_table_names():
        return
    existing = {item["name"] for item in sa.inspect(bind).get_columns("questions")}
    for name in ("words_per_minute", "filler_word_count", "spoken_word_count", "speech_duration_seconds"):
        if name in existing:
            op.drop_column("questions", name)