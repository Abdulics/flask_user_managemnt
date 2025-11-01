import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date, timedelta
from .. import db, create_app
from ..models.user import User, team_members
from ..models.team import Team
from ..models.task import Task
from ..models.address import Address
from ..models.employees import Employee
from ..models.timeoff import TimeOff, TimeOffType, TimeOffStatus
from ..models.attendance import Attendance, AttendanceStatus

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
		User(username="alice", email="alice@example.com", is_admin=True, bio="Admin user"),
		User(username="bob", email="bob@example.com", bio="Regular user"),
		User(username="carol", email="carol@example.com", bio="Manager user"),
		User(username="dave", email="dave@example.com", bio="Developer"),
		User(username="eve", email="eve@example.com", bio="Intern")
	]

	for u in users:
		u.password = "password123"  # hashed automatically
		db.session.add(u)

	db.session.commit()

	# --- TEAMS ---
	team1 = Team(name="Engineering", slug="engineering", description="Engineering team", owner_id=users[0].id)
	team2 = Team(name="HR", slug="hr", description="HR team", owner_id=users[2].id)
	db.session.add_all([team1, team2])
	db.session.commit()

	# Add members
	team1.add_member(users[1])
	team1.add_member(users[3])
	team2.add_member(users[2])
	team2.add_member(users[4])
	db.session.commit()

	# --- EMPLOYEES ---
	employees = [
		Employee(user_id=users[0].id, employee_id="E001", first_name="Alice", last_name="Admin", department="IT", position="CTO", salary=150000),
		Employee(user_id=users[1].id, employee_id="E002", first_name="Bob", last_name="Builder", department="Engineering", position="Engineer", salary=90000, manager_id=1),
		Employee(user_id=users[2].id, employee_id="E003", first_name="Carol", last_name="Manager", department="HR", position="HR Manager", salary=95000),
		Employee(user_id=users[3].id, employee_id="E004", first_name="Dave", last_name="Dev", department="Engineering", position="Developer", salary=85000, manager_id=2),
		Employee(user_id=users[4].id, employee_id="E005", first_name="Eve", last_name="Intern", department="HR", position="Intern", salary=40000, manager_id=3)
	]
	db.session.add_all(employees)
	db.session.commit()

	# --- ADDRESSES ---
	addresses = [
		Address(employee_id=1, type="home", street="123 Admin St", city="New York", state="NY", postal_code="10001", country="USA"),
		Address(employee_id=2, type="home", street="456 Builder Ave", city="Boston", state="MA", postal_code="02110", country="USA"),
		Address(employee_id=3, type="home", street="789 Manager Rd", city="Chicago", state="IL", postal_code="60601", country="USA"),
	]
	db.session.add_all(addresses)
	db.session.commit()

	# --- TASKS ---
	tasks = [
		Task(title="Setup project repo", description="Initialize GitLab repo", user_id=users[1].id, due_date=datetime.utcnow() + timedelta(days=3)),
		Task(title="Create HR policy", description="Draft HR guidelines", user_id=users[2].id, due_date=datetime.utcnow() + timedelta(days=5)),
		Task(title="Develop API", description="REST API endpoints", user_id=users[3].id, due_date=datetime.utcnow() + timedelta(days=7)),
		Task(title="Prepare presentation", description="Team presentation slides", user_id=users[4].id, due_date=datetime.utcnow() + timedelta(days=2)),
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
	# attendances = []
	# for u in users:
	#     for i in range(5):  # last 5 days
	#         attendances.append(Attendance(user_id=u.id, date=date.today() - timedelta(days=i), status=AttendanceStatus.PRESENT))

	# db.session.add_all(attendances)
	# db.session.commit()

	print("Sample data inserted successfully!")
