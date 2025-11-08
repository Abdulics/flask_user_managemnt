import sys
import os

# Add project root to Python path (add parent of 'app' so absolute imports work)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, date, timedelta
from app import db, create_app
from app.models.user import Role, User
from app.models.team import Team
from app.models.task import Task
from app.models.address import Address
from app.models.employees import Employee
from app.models.timeoff import TimeOff, TimeOffType, TimeOffStatus
from app.models.attendance import Attendance, AttendanceStatus

app = create_app()

with app.app_context():
	# # Clear existing data (optional, careful in production!)
	# db.session.execute(team_members.delete())
	# #Attendance.query.delete()
	# TimeOff.query.delete()
	# Task.query.delete()
	# Address.query.delete()
	# Employee.query.delete()
	# Team.query.delete()
	# User.query.delete()
	# db.session.commit()

	# --- USERS ---
	users = [
		User(username="alice", email="alice@example.com", bio="Admin user", role=Role.ADMIN),
		User(username="bob", email="bob@example.com", bio="Regular user"),
		User(username="carol", email="carol@example.com", bio="Manager user", role=Role.MANAGER),
		User(username="dave", email="dave@example.com", bio="Developer", role=Role.EMPLOYEE),
		User(username="eve", email="eve@example.com", bio="Intern"),
		User(username="frank", email="frank@example,com", bio="IT-manager", role=Role.MANAGER)
	]

	for u in users:
		u.password = "password123"  # hashed automatically
		db.session.add(u)

	db.session.commit()

	# --- TEAMS ---
	team1 = Team(name="Engineering", slug="engineering", description="Engineering team", owner_id=users[0].id)
	team2 = Team(name="HR", slug="hr", description="HR team", owner_id=users[2].id)
	team3 = Team(name="IT", slug="it", description="IT team", owner_id=users[5].id)
	db.session.add_all([team1, team2, team3])
	db.session.commit()

	# Add members
	team1.add_member(users[1])
	team1.add_member(users[3])
	team2.add_member(users[2])
	team2.add_member(users[4])
	team3.add_member(users[0])
	team3.add_member(users[5])
	db.session.commit()

	# --- EMPLOYEES ---
	employees = [
		Employee(user_id=users[0].id, employee_id="E001", first_name="Alice", last_name="Admin", department="IT", position="CTO", salary=150000),
		Employee(user_id=users[1].id, employee_id="E002", first_name="Bob", last_name="Builder", department="Engineering", position="Engineer", salary=90000, manager_id=1),
		Employee(user_id=users[2].id, employee_id="E003", first_name="Carol", last_name="Manager", department="HR", position="HR Manager", salary=95000),
		Employee(user_id=users[3].id, employee_id="E004", first_name="Dave", last_name="Dev", department="Engineering", position="Developer", salary=85000, manager_id=2),
		Employee(user_id=users[4].id, employee_id="E005", first_name="Eve", last_name="Intern", department="HR", position="Intern", salary=40000, manager_id=3),
		Employee(user_id=users[5].id, employee_id="E006", first_name="Frank", last_name="IT", department="IT", position="IT Manager", salary=95000)
	]
	db.session.add_all(employees)
	db.session.commit()

	# --- ADDRESSES ---
	addresses = [
		Address(employee_id=1, type="home", street="123 Admin St", city="New York", state="NY", postal_code="10001", country="USA"),
		Address(employee_id=2, type="home", street="456 Builder Ave", city="Boston", state="MA", postal_code="02110", country="USA"),
		Address(employee_id=3, type="home", street="789 Manager Rd", city="Chicago", state="IL", postal_code="60601", country="USA"),
		Address(employee_id=4, type="home", street="321 Dev Blvd", city="San Francisco", state="CA", postal_code="94105", country="USA"),
		Address(employee_id=5, type="home", street="654 Intern Ln", city="Seattle", state="WA", postal_code="98101", country="USA"),
		Address(employee_id=6, type="home", street="987 IT St", city="Austin", state="TX", postal_code="73301", country="USA")
	]
	db.session.add_all(addresses)
	db.session.commit()

	# --- TASKS ---
	tasks = [
		Task(title="Setup project repo", description="Initialize GitLab repo", user_id=users[1].id, due_date=datetime.utcnow() + timedelta(days=3)),
		Task(title="Create HR policy", description="Draft HR guidelines", user_id=users[2].id, due_date=datetime.utcnow() + timedelta(days=5)),
		Task(title="Develop API", description="REST API endpoints", user_id=users[3].id, due_date=datetime.utcnow() + timedelta(days=7)),
		Task(title="Prepare presentation", description="Team presentation slides", user_id=users[4].id, due_date=datetime.utcnow() + timedelta(days=2)),
		Task(title="Upgrade servers", description="Update server OS and software", user_id=users[5].id, due_date=datetime.utcnow() + timedelta(days=4))
	]
	db.session.add_all(tasks)
	db.session.commit()

	# --- TIME OFFS ---
	timeoffs = [
		TimeOff(user_id=users[1].id, type=TimeOffType.VACATION, status=TimeOffStatus.APPROVED, start_date=date.today() + timedelta(days=10), end_date=date.today() + timedelta(days=15), reason="Family vacation"),
		TimeOff(user_id=users[3].id, type=TimeOffType.SICK, status=TimeOffStatus.PENDING, start_date=date.today() + timedelta(days=1), end_date=date.today() + timedelta(days=3), reason="Medical leave"),
	]
	db.session.add_all(timeoffs)
	db.session.commit()

	# --- ATTENDANCE ---
	attendances = []
	for u in users:
		for i in range(5):  # last 5 days
			attendances.append(Attendance(user_id=u.id, date=date.today() - timedelta(days=i), status=AttendanceStatus.PRESENT))


	db.session.add_all(attendances)
	db.session.commit()

	print("Sample data inserted successfully!")
