"""initial postgresql schema

Revision ID: 20260526_0001
Revises:
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa


revision = "20260526_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_blogs_id"), "blogs", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("person_name", sa.String(length=120), nullable=True),
        sa.Column("birth_date", sa.String(length=20), nullable=True),
        sa.Column("birth_time", sa.String(length=20), nullable=True),
        sa.Column("birth_city", sa.String(length=120), nullable=True),
        sa.Column("accuracy", sa.String(length=40), nullable=True),
        sa.Column("experience", sa.String(length=40), nullable=True),
        sa.Column("usefulness", sa.String(length=40), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_created_at"), "feedback", ["created_at"], unique=False)
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
    op.create_index(op.f("ix_feedback_user_id"), "feedback", ["user_id"], unique=False)

    op.create_table(
        "user_activities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_activities_id"), "user_activities", ["id"], unique=False)
    op.create_index(op.f("ix_user_activities_user_id"), "user_activities", ["user_id"], unique=False)

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("birth_date", sa.String(length=20), nullable=True),
        sa.Column("birth_time", sa.String(length=20), nullable=True),
        sa.Column("birth_city", sa.String(length=120), nullable=True),
        sa.Column("zodiac_sign", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_profiles_id"), "user_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_user_profiles_user_id"), "user_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_profiles_user_id"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_id"), table_name="user_profiles")
    op.drop_table("user_profiles")
    op.drop_index(op.f("ix_user_activities_user_id"), table_name="user_activities")
    op.drop_index(op.f("ix_user_activities_id"), table_name="user_activities")
    op.drop_table("user_activities")
    op.drop_index(op.f("ix_feedback_user_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_created_at"), table_name="feedback")
    op.drop_table("feedback")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_blogs_id"), table_name="blogs")
    op.drop_table("blogs")
