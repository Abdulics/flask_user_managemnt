import os
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from app.models.address import Address
from app.models.attendance import Attendance, AttendanceStatus
from app.models.department import Department
from app.models.employees import Employee, Role
from app.models.message import Message
from app.models.paystub import Paystub
from app.models.task import Task
from app.models.team import Team
from app.models.time_entry import TimeEntry
from app.models.timeoff import TimeOff, TimeOffStatus, TimeOffType
from app.models.user import User


DEFAULT_PASSWORD = "password123"


app = create_app()


def get_or_create(model, defaults=None, **filters):
    instance = model.query.filter_by(**filters).first()
    if instance:
        return instance
    data = dict(filters)
    if defaults:
        data.update(defaults)
    instance = model(**data)
    db.session.add(instance)
    db.session.flush()
    return instance


def create_user(username, employee):
    user = User.query.filter_by(username=username).first()
    if user:
        user.employee_id = employee.id
        user.email = employee.email
        user.is_active = True
        return user
    user = User(username=username, email=employee.email, employee_id=employee.id)
    user.set_password(DEFAULT_PASSWORD)
    db.session.add(user)
    db.session.flush()
    return user


def add_address(employee, street, city, state, postal_code):
    if employee.addresses:
        return employee.addresses[0]
    address = Address(
        employee_id=employee.id,
        type="Home",
        street=street,
        city=city,
        state=state,
        postal_code=postal_code,
        country="United States",
    )
    db.session.add(address)
    db.session.flush()
    return address


def add_task(title, assignee, creator, status, priority, due_offset, description):
    task = Task.query.filter_by(title=title, assigned_to_id=assignee.id).first()
    if task:
        return task
    now = datetime.now(timezone.utc)
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        assigned_to_id=assignee.id,
        created_by_id=creator.id,
        due_date=now + timedelta(days=due_offset),
        completed_at=now - timedelta(days=1) if status == "completed" else None,
    )
    db.session.add(task)
    return task


def add_attendance(user, day_offset, status, note=None):
    target_date = date.today() + timedelta(days=day_offset)
    record = Attendance.for_user_on_date(user.id, target_date, create_if_missing=True)
    record.status = status
    record.note = note
    db.session.add(record)
    return record


def add_time_entry(user, clock_in, hours=None):
    existing = TimeEntry.query.filter_by(user_id=user.id, clock_in=clock_in).first()
    if existing:
        return existing
    entry = TimeEntry(user_id=user.id, clock_in=clock_in)
    if hours is not None:
        entry.clock_out = clock_in + timedelta(hours=hours)
    db.session.add(entry)
    return entry


def add_timeoff(user, manager, status, start_offset, days, request_type, reason, hr=None):
    start = date.today() + timedelta(days=start_offset)
    end = start + timedelta(days=days - 1)
    existing = TimeOff.query.filter_by(user_id=user.id, start_date=start, end_date=end).first()
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    request = TimeOff(
        user_id=user.id,
        manager_id=manager.id if manager else None,
        hr_id=hr.id if status in [TimeOffStatus.APPROVED, TimeOffStatus.DENIED] and hr else None,
        type=request_type,
        status=status,
        start_date=start,
        end_date=end,
        reason=reason,
    )
    if status in [TimeOffStatus.MANAGER_APPROVED, TimeOffStatus.APPROVED, TimeOffStatus.DENIED]:
        request.manager_decision_at = now - timedelta(days=1)
    if status in [TimeOffStatus.APPROVED, TimeOffStatus.DENIED]:
        request.hr_decision_at = now
    db.session.add(request)
    return request


def add_message(sender, recipient, subject, body, is_read=False):
    existing = Message.query.filter_by(sender_id=sender.id, recipient_id=recipient.id, subject=subject).first()
    if existing:
        return existing
    msg = Message(
        sender_id=sender.id,
        recipient_id=recipient.id,
        subject=subject,
        body=body,
        is_read=is_read,
    )
    db.session.add(msg)
    return msg


def add_paystub(employee, period_start, gross, taxes, deductions):
    period_end = period_start + timedelta(days=13)
    existing = Paystub.query.filter_by(employee_id=employee.id, pay_period_start=period_start).first()
    if existing:
        return existing
    paystub = Paystub(
        employee_id=employee.id,
        pay_period_start=period_start,
        pay_period_end=period_end,
        gross_pay=Decimal(str(gross)),
        taxes=Decimal(str(taxes)),
        deductions=Decimal(str(deductions)),
        issued_at=datetime.now(timezone.utc),
        notes="Demo payroll record",
    )
    paystub.calculate_net_pay()
    db.session.add(paystub)
    return paystub


with app.app_context():
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        raise RuntimeError("Default admin not found. Run `flask init-db` before seeding demo data.")

    hr_dept = get_or_create(Department, name="Human Resources", defaults={"description": "Hiring, people operations, benefits, and HR approvals"})
    it_dept = get_or_create(Department, name="Information Technology", defaults={"description": "Systems, infrastructure, and internal support"})
    sales_dept = get_or_create(Department, name="Sales", defaults={"description": "Client relations and revenue operations"})
    finance_dept = get_or_create(Department, name="Finance", defaults={"description": "Payroll, budgeting, and accounting"})
    db.session.commit()

    recruitment = get_or_create(Team, name="Recruitment Team", defaults={"description": "Hiring and onboarding", "department_id": hr_dept.id})
    employee_relations = get_or_create(Team, name="Employee Relations Team", defaults={"description": "Policies, benefits, and employee support", "department_id": hr_dept.id})
    helpdesk = get_or_create(Team, name="Helpdesk Support Team", defaults={"description": "Internal tickets and support", "department_id": it_dept.id})
    infrastructure = get_or_create(Team, name="Infrastructure Team", defaults={"description": "Network and server operations", "department_id": it_dept.id})
    corporate_sales = get_or_create(Team, name="Corporate Sales Team", defaults={"description": "Enterprise accounts", "department_id": sales_dept.id})
    payroll = get_or_create(Team, name="Payroll Team", defaults={"description": "Payroll processing and paystub support", "department_id": finance_dept.id})
    db.session.commit()

    hr_manager = get_or_create(Employee, email="sarah.hr@teammanager.com", defaults={
        "first_name": "Sarah", "last_name": "Thompson", "phone": "555-1001", "position": "HR Manager",
        "role": Role.MANAGER, "hire_date": date.today() - timedelta(days=900), "department_id": hr_dept.id,
        "team_id": recruitment.id,
    })
    it_manager = get_or_create(Employee, email="james.it@teammanager.com", defaults={
        "first_name": "James", "last_name": "Lee", "phone": "555-2001", "position": "IT Manager",
        "role": Role.MANAGER, "hire_date": date.today() - timedelta(days=820), "department_id": it_dept.id,
        "team_id": infrastructure.id,
    })
    hr_emp = get_or_create(Employee, email="linda.hr@teammanager.com", defaults={
        "first_name": "Linda", "last_name": "Perez", "phone": "555-1010", "position": "HR Specialist",
        "role": Role.EMPLOYEE, "hire_date": date.today() - timedelta(days=330), "department_id": hr_dept.id,
        "manager_id": hr_manager.id, "team_id": employee_relations.id,
    })
    it_emp = get_or_create(Employee, email="michael.it@teammanager.com", defaults={
        "first_name": "Michael", "last_name": "Green", "phone": "555-2010", "position": "IT Support Specialist",
        "role": Role.EMPLOYEE, "hire_date": date.today() - timedelta(days=280), "department_id": it_dept.id,
        "manager_id": it_manager.id, "team_id": helpdesk.id,
    })
    sales_emp = get_or_create(Employee, email="kevin.sales@teammanager.com", defaults={
        "first_name": "Kevin", "last_name": "Roberts", "phone": "555-3005", "position": "Sales Representative",
        "role": Role.EMPLOYEE, "hire_date": date.today() - timedelta(days=190), "department_id": sales_dept.id,
        "manager_id": hr_manager.id, "team_id": corporate_sales.id,
    })
    finance_emp = get_or_create(Employee, email="hannah.finance@teammanager.com", defaults={
        "first_name": "Hannah", "last_name": "Williams", "phone": "555-4005", "position": "Payroll Accountant",
        "role": Role.EMPLOYEE, "hire_date": date.today() - timedelta(days=240), "department_id": finance_dept.id,
        "manager_id": hr_manager.id, "team_id": payroll.id,
    })

    # Keep the familiar sample users, but wire them into practical manager/team flows.
    sarah_user = create_user("sarah_hr", hr_manager)
    james_user = create_user("james_it", it_manager)
    linda_user = create_user("linda_hr", hr_emp)
    michael_user = create_user("michael_it", it_emp)
    kevin_user = create_user("kevin_sales", sales_emp)
    hannah_user = create_user("hannah_finance", finance_emp)

    recruitment.lead_id = hr_manager.id
    employee_relations.lead_id = hr_manager.id
    infrastructure.lead_id = it_manager.id
    helpdesk.lead_id = it_manager.id
    corporate_sales.lead_id = sales_emp.id
    payroll.lead_id = finance_emp.id

    add_address(hr_manager, "45 Oakwood Lane", "Aurora", "IL", "60504")
    add_address(it_manager, "90 Maple Ridge", "Naperville", "IL", "60540")
    add_address(hr_emp, "12 Willow Street", "Bolingbrook", "IL", "60440")
    add_address(it_emp, "8 Ridgeview Drive", "Chicago", "IL", "60616")
    add_address(sales_emp, "200 Lakeview Pkwy", "Schaumburg", "IL", "60173")
    add_address(finance_emp, "333 Brookside Ave", "Wheaton", "IL", "60187")
    db.session.commit()

    now = datetime.now(timezone.utc)

    add_task("Prepare onboarding checklist", linda_user, sarah_user, "in_progress", "medium", 5, "Update the onboarding checklist for next week's new hire.")
    add_task("Review benefits enrollment queue", linda_user, sarah_user, "pending", "high", 2, "Check pending benefits enrollment submissions and follow up.")
    add_task("Patch helpdesk laptops", michael_user, james_user, "pending", "high", 3, "Patch laptops waiting in the helpdesk queue.")
    add_task("Verify nightly backup report", michael_user, james_user, "completed", "medium", -1, "Confirm last night's backup status and file a short note.")
    add_task("Follow up with Acme account", kevin_user, admin_user, "in_progress", "medium", 4, "Send a follow-up summary and next-step proposal.")
    add_task("Prepare payroll variance notes", hannah_user, admin_user, "pending", "high", 6, "Summarize payroll variance items for leadership review.")
    add_task("Run system access audit", james_user, admin_user, "in_progress", "high", 10, "Review active admin accounts and stale permissions.")
    add_task("Draft HR policy update", sarah_user, admin_user, "pending", "medium", 12, "Draft an updated remote-work policy for review.")

    for user in [sarah_user, james_user, linda_user, michael_user, kevin_user, hannah_user]:
        add_attendance(user, -2, AttendanceStatus.PRESENT)
        add_attendance(user, -1, AttendanceStatus.LATE if user == kevin_user else AttendanceStatus.PRESENT, "Client meeting ran late" if user == kevin_user else None)
        add_attendance(user, 0, AttendanceStatus.PRESENT)

    add_time_entry(linda_user, now - timedelta(days=2, hours=8), 7.5)
    add_time_entry(linda_user, now - timedelta(days=1, hours=8), 8)
    add_time_entry(michael_user, now - timedelta(days=1, hours=9), 6.75)
    add_time_entry(kevin_user, now - timedelta(days=1, hours=7), 7.25)
    add_time_entry(hannah_user, now - timedelta(days=3, hours=8), 8)
    add_time_entry(sarah_user, now - timedelta(hours=2), None)

    add_timeoff(linda_user, sarah_user, TimeOffStatus.PENDING, 9, 2, TimeOffType.VACATION, "Family trip request")
    add_timeoff(michael_user, james_user, TimeOffStatus.MANAGER_APPROVED, 14, 1, TimeOffType.SICK, "Medical appointment")
    add_timeoff(kevin_user, sarah_user, TimeOffStatus.APPROVED, -10, 3, TimeOffType.VACATION, "Approved vacation demo record", hr=sarah_user)
    add_timeoff(hannah_user, sarah_user, TimeOffStatus.DENIED, 20, 2, TimeOffType.OTHER, "Coverage conflict demo record", hr=sarah_user)

    add_message(admin_user, sarah_user, "Demo data ready", "The demo workspace has seeded teams, tasks, attendance, time off, and paystubs.", True)
    add_message(sarah_user, linda_user, "Onboarding task", "Please review the onboarding checklist before Friday.", False)
    add_message(james_user, michael_user, "Backup report", "Can you verify the latest backup report today?", False)
    add_message(linda_user, sarah_user, "Time off submitted", "I submitted a vacation request for next week.", False)
    add_message(hannah_user, admin_user, "Payroll ready", "The sample payroll reports are ready for review.", True)

    period_start = date.today() - timedelta(days=21)
    payroll_rows = [
        (hr_manager, "4200.00", "820.00", "125.00"),
        (it_manager, "4400.00", "860.00", "130.00"),
        (hr_emp, "2850.00", "510.00", "90.00"),
        (it_emp, "3000.00", "545.00", "95.00"),
        (sales_emp, "2750.00", "480.00", "80.00"),
        (finance_emp, "3100.00", "575.00", "100.00"),
    ]
    for employee, gross, taxes, deductions in payroll_rows:
        add_paystub(employee, period_start, gross, taxes, deductions)

    db.session.commit()

    print("Demo data seeded successfully.")
    print("Default admin remains: admin / admin123")
    print("Sample user password: password123")
