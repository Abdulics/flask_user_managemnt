"""Lowercase attendance_status enum values

Revision ID: 9b0e2e1c1a2f
Revises: 5fb6cf01cad8
Create Date: 2025-11-22 03:35:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b0e2e1c1a2f'
down_revision = '6fa153544bf5'
branch_labels = None
depends_on = None


def upgrade():
    # No-op: retain uppercase enum values present in initial schema.
    pass


def downgrade():
    pass
