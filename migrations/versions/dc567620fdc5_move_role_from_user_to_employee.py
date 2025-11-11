"""Move role from User to Employee

Revision ID: dc567620fdc5
Revises: e31e216a9778
Create Date: 2025-11-10 21:18:07.793245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dc567620fdc5'
down_revision = 'e31e216a9778'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column first
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.Enum('ADMIN', 'MANAGER', 'EMPLOYEE', name='role'), nullable=True))

    # Copy data from user → employees
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE employees
        SET role = u.role
        FROM "user" AS u
        WHERE u.employee_id = employees.id
    """))

    # Fill any remaining NULL roles with default value (EMPLOYEE)
    connection.execute(sa.text("""
        UPDATE employees
        SET role = 'EMPLOYEE'
        WHERE role IS NULL
    """))

    # Now make the role column NOT NULL
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.alter_column('role', nullable=False)

    # Finally drop from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('role')


def downgrade():
    # Add the column back to user
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.Enum('ADMIN', 'MANAGER', 'EMPLOYEE', name='role'), nullable=True))

    # Move the data back (if downgrading)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE "user"
        SET role = e.role
        FROM employees AS e
        WHERE e.id = "user".employee_id
    """))

    connection.execute(sa.text("""
        UPDATE "user"
        SET role = 'EMPLOYEE'
        WHERE role IS NULL
    """))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('role', nullable=False)

    # Drop the column from employees
    with op.batch_alter_table('employees', schema=None) as batch_op:
        batch_op.drop_column('role')

