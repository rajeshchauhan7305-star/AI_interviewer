"""Add user-owned resume analysis and job-description matches.

Revision ID: 20260926_02
Revises: 20260926_01
Create Date: 2026-09-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260926_02"
down_revision = "20260926_01"
branch_labels = None
depends_on = None


def upgrade():
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "resumes" not in tables:
        op.create_table(
            "resumes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("content_type", sa.String(length=120), nullable=False),
            sa.Column("extracted_text", sa.Text(), nullable=False),
            sa.Column("profile_json", sa.Text(), nullable=False),
            sa.Column("analysis_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_resumes_user_created", "resumes", ["user_id", "created_at"])

    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "job_descriptions" not in tables:
        op.create_table(
            "job_descriptions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("resume_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=120), nullable=False, server_default="Job description"),
            sa.Column("description_text", sa.Text(), nullable=False),
            sa.Column("match_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
            sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_job_descriptions_user_created", "job_descriptions", ["user_id", "created_at"])


def downgrade():
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "job_descriptions" in tables:
        indexes = {item["name"] for item in sa.inspect(op.get_bind()).get_indexes("job_descriptions")}
        if "ix_job_descriptions_user_created" in indexes:
            op.drop_index("ix_job_descriptions_user_created", table_name="job_descriptions")
        op.drop_table("job_descriptions")
    if "resumes" in tables:
        indexes = {item["name"] for item in sa.inspect(op.get_bind()).get_indexes("resumes")}
        if "ix_resumes_user_created" in indexes:
            op.drop_index("ix_resumes_user_created", table_name="resumes")
        op.drop_table("resumes")