"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-03

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("preferred_language", sa.String(length=2), nullable=False, server_default="de"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=False),
        sa.Column("energy_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_journal_entries_user_id", "journal_entries", ["user_id"], unique=False)

    op.create_table(
        "entry_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "entry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("journal_entries.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.Column("emotions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("themes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pillar_weights", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pillar_scores", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reflection", sa.Text(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("signals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rationale_summary", sa.Text(), nullable=False),
        sa.Column("risk_flags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_entry_analysis_entry_id", "entry_analysis", ["entry_id"], unique=True)
    op.create_index("ix_entry_analysis_user_id", "entry_analysis", ["user_id"], unique=False)

    op.create_table(
        "weekly_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("week_end_date", sa.Date(), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False),
        sa.Column("pillar_scores_avg", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pillar_trends", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recurring_patterns", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("correlations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("daily_recommendation", sa.Text(), nullable=False),
        sa.Column("weekly_goal", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_weekly_reports_user_id", "weekly_reports", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_weekly_reports_user_id", table_name="weekly_reports")
    op.drop_table("weekly_reports")

    op.drop_index("ix_entry_analysis_user_id", table_name="entry_analysis")
    op.drop_index("ix_entry_analysis_entry_id", table_name="entry_analysis")
    op.drop_table("entry_analysis")

    op.drop_index("ix_journal_entries_user_id", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
