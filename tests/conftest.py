import os
import tempfile
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app import create_app, db
from app.models.department import Department
from app.models.employees import Employee, Role
from app.models.message import Message
from app.models.paystub import Paystub
from app.models.task import Task
from app.models.team import Team
from app.models.time_entry import TimeEntry
from app.models.timeoff import TimeOff, TimeOffStatus, TimeOffType
from app.models.user import User


@pytest.fixture
def app():
    fd, db_path = tempfile.mkstemp(prefix="team_manager_test_", suffix=".sqlite")
    test_app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with test_app.app_context():
        db.create_all()
        seed_basic_data()

    yield test_app

    with test_app.app_context():
        db.session.remove()
        db.engine.dispose()

    os.close(fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    return app.test_client()


def make_user(username, role, department, manager=None, team=None):
    employee = Employee(
        first_name=username.title(),
        last_name="User",
        email=f"{username}@example.com",
        role=role,
        position=role.value.title(),
        hire_date=date.today(),
        department_id=department.id,
        manager_id=manager.id if manager else None,
        team_id=team.id if team else None,
    )
    db.session.add(employee)
    db.session.flush()

    user = User(username=username, email=employee.email, employee_id=employee.id)
    user.set_password("password123")
    db.session.add(user)
    db.session.flush()
    return user


def seed_basic_data():
    hr = Department(name="Human Resources", description="People operations")
    it = Department(name="Information Technology", description="IT")
    db.session.add_all([hr, it])
    db.session.flush()

    ops_team = Team(name="Operations Team", department_id=hr.id)
    it_team = Team(name="IT Team", department_id=it.id)
    db.session.add_all([ops_team, it_team])
    db.session.flush()

    admin = make_user("admin", Role.ADMIN, hr, team=ops_team)
    admin.set_password("admin123")
    manager = make_user("manager", Role.MANAGER, it, team=it_team)
    employee = make_user("employee", Role.EMPLOYEE, it, manager=manager.employee, team=it_team)
    other = make_user("other", Role.EMPLOYEE, hr, team=ops_team)
    hr_user = make_user("hr_user", Role.EMPLOYEE, hr, team=ops_team)

    ops_team.lead_id = admin.employee.id
    it_team.lead_id = manager.employee.id

    db.session.add(Task(
        title="Existing Task",
        description="Assigned task",
        status="pending",
        priority="medium",
        assigned_to_id=employee.id,
        created_by_id=manager.id,
        due_date=datetime.now(timezone.utc) + timedelta(days=3),
    ))

    db.session.add(TimeEntry(
        user_id=employee.id,
        clock_in=datetime.now(timezone.utc) - timedelta(hours=1),
        clock_out=datetime.now(timezone.utc),
    ))

    paystub = Paystub(
        employee_id=employee.employee.id,
        pay_period_start=date.today() - timedelta(days=14),
        pay_period_end=date.today() - timedelta(days=1),
        gross_pay=Decimal("1000.00"),
        taxes=Decimal("150.00"),
        deductions=Decimal("50.00"),
        issued_at=datetime.now(timezone.utc),
    )
    paystub.calculate_net_pay()
    db.session.add(paystub)

    db.session.add(TimeOff(
        user_id=employee.id,
        manager_id=manager.id,
        type=TimeOffType.VACATION,
        status=TimeOffStatus.PENDING,
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6),
        reason="Pending manager review",
    ))
    db.session.add(TimeOff(
        user_id=other.id,
        manager_id=admin.id,
        type=TimeOffType.SICK,
        status=TimeOffStatus.MANAGER_APPROVED,
        start_date=date.today() + timedelta(days=8),
        end_date=date.today() + timedelta(days=8),
        reason="HR queue item",
    ))

    db.session.add(Message(sender_id=admin.id, recipient_id=employee.id, subject="Welcome", body="Hello"))
    db.session.commit()


def login(client, username, password="password123"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
