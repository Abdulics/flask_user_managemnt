"""add employee team membership

Revision ID: b8e2f1c4d6a9
Revises: a7d4c9e8b2f1
Create Date: 2026-05-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b8e2f1c4d6a9"
down_revision = "a7d4c9e8b2f1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.add_column(sa.Column("team_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_employees_team_id_team", "team", ["team_id"], ["id"])


def downgrade():
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.drop_constraint("fk_employees_team_id_team", type_="foreignkey")
        batch_op.drop_column("team_id")
