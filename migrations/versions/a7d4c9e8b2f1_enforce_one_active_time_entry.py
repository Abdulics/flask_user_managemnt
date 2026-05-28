"""enforce one active time entry per user

Revision ID: a7d4c9e8b2f1
Revises: 3cdd7e4c559d
Create Date: 2026-05-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a7d4c9e8b2f1"
down_revision = "3cdd7e4c559d"
branch_labels = None
depends_on = None


def upgrade():
    # Keep the newest active entry per user active; close any older duplicate
    # active rows so the partial unique index can be created successfully.
    op.execute(
        sa.text(
            """
            WITH ranked_active_entries AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY user_id
                        ORDER BY clock_in DESC, id DESC
                    ) AS row_number
                FROM time_entries
                WHERE clock_out IS NULL
            )
            UPDATE time_entries
            SET clock_out = clock_in,
                updated_at = NOW()
            WHERE id IN (
                SELECT id
                FROM ranked_active_entries
                WHERE row_number > 1
            )
            """
        )
    )

    op.create_index(
        "uix_time_entries_one_active_per_user",
        "time_entries",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("clock_out IS NULL"),
    )


def downgrade():
    op.drop_index(
        "uix_time_entries_one_active_per_user",
        table_name="time_entries",
        postgresql_where=sa.text("clock_out IS NULL"),
    )
