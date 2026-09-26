"""Add persisted personalized study plans.

Revision ID: 20260926_03
Revises: 20260926_02
Create Date: 2026-09-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260926_03"
down_revision = "20260926_02"
branch_labels = None
depends_on = None


def upgrade():
    if "study_plans" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "study_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("tasks_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_study_plans_user_created", "study_plans", ["user_id", "created_at"])


def downgrade():
    if "study_plans" not in sa.inspect(op.get_bind()).get_table_names():
        return
    indexes = {item["name"] for item in sa.inspect(op.get_bind()).get_indexes("study_plans")}
    if "ix_study_plans_user_created" in indexes:
        op.drop_index("ix_study_plans_user_created", table_name="study_plans")
    op.drop_table("study_plans")