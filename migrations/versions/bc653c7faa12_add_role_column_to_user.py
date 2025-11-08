"""add role column to User

Revision ID: bc653c7faa12
Revises: 7f1ec31cab16
Create Date: 2025-11-07 17:19:04.703023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc653c7faa12'
down_revision = '7f1ec31cab16'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # create the enum type first
    role_enum = postgresql.ENUM('ADMIN', 'MANAGER', 'EMPLOYEE', name='role')
    role_enum.create(op.get_bind(), checkfirst=True)  # checkfirst avoids duplicates

    # then add the column
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('role', role_enum, nullable=False, server_default='EMPLOYEE')
        )
        batch_op.drop_column('is_admin')


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False))
        batch_op.drop_column('role')

    # drop the enum type
    role_enum = postgresql.ENUM('ADMIN', 'MANAGER', 'EMPLOYEE', name='role')
    role_enum.drop(op.get_bind(), checkfirst=True)


    # ### end Alembic commands ###
