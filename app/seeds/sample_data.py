import sys
import os

# Add project root to Python path (add parent of 'app' so absolute imports work)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, date, timedelta, timezone
from app import db, create_app
from app.models.user import Role, User
from app.models.department import Department
from app.models.team import Team
from app.models.task import Task
from app.models.address import Address
from app.models.employees import Employee
from app.models.timeoff import TimeOff, TimeOffType, TimeOffStatus
from app.models.attendance import Attendance, AttendanceStatus

app = create_app()

with app.app_context():
	from datetime import date, datetime, timezone

	### --- Departments ---
	hr_dept = Department(name='Human Resources', description='Handles employee relations')
	it_dept = Department(name='Information Technology', description='IT & System Support')
	sales_dept = Department(name='Sales', description='Sales and client relations')
	finance_dept = Department(name='Finance', description='Finance & Accounting')

	db.session.add_all([hr_dept, it_dept, sales_dept, finance_dept])
	db.session.commit()



	# ------------------------------------------------------------------------------------
	# ---------------------------------- TEAMS -------------------------------------------
	# ------------------------------------------------------------------------------------

	teams = []

	# HR Teams
	teams.append(Team(
		name='Recruitment Team',
		description='Handles hiring and onboarding new employees',
		department_id=hr_dept.id
	))

	teams.append(Team(
		name='Employee Relations Team',
		description='Handles conflict resolution and internal policies',
		department_id=hr_dept.id
	))

	# IT Teams
	teams.append(Team(
		name='Helpdesk Support Team',
		description='Handles support tickets and troubleshooting',
		department_id=it_dept.id
	))

	teams.append(Team(
		name='Infrastructure Team',
		description='Maintains network and server infrastructure',
		department_id=it_dept.id
	))

	# Sales Teams
	teams.append(Team(
		name='Corporate Sales Team',
		description='Handles corporate accounts',
		department_id=sales_dept.id
	))

	teams.append(Team(
		name='Retail Sales Team',
		description='Handles retail customer accounts',
		department_id=sales_dept.id
	))

	# Finance Teams
	teams.append(Team(
		name='Budgeting Team',
		description='Manages budgets and forecasts',
		department_id=finance_dept.id
	))

	teams.append(Team(
		name='Payroll Team',
		description='Handles payroll operations',
		department_id=finance_dept.id
	))

	db.session.add_all(teams)
	db.session.commit()



	# ------------------------------------------------------------------------------------
	# ---------------------------------- EMPLOYEES ---------------------------------------
	# ------------------------------------------------------------------------------------


	### --- HR MANAGER ---
	hr_manager = Employee(
		first_name='Sarah',
		last_name='Thompson',
		email='sarah.hr@teammanager.com',
		phone='555-1001',
		position='HR Manager',
		role=Role.MANAGER,
		hire_date=date.today(),
		department_id=hr_dept.id
	)
	db.session.add(hr_manager)
	db.session.commit()

	db.session.add(Address(
		employee_id=hr_manager.id,
		type='Home',
		street='45 Oakwood Lane',
		city='Aurora',
		state='IL',
		postal_code='60504',
		country='USA'
	))
	db.session.commit()

	# Assign as lead of Recruitment Team
	teams[0].lead_id = hr_manager.id
	db.session.commit()



	### --- IT MANAGER ---
	it_manager = Employee(
		first_name='James',
		last_name='Lee',
		email='james.it@teammanager.com',
		phone='555-2001',
		position='IT Manager',
		role=Role.MANAGER,
		hire_date=date.today(),
		department_id=it_dept.id
	)
	db.session.add(it_manager)
	db.session.commit()

	db.session.add(Address(
		employee_id=it_manager.id,
		type='Home',
		street='90 Maple Ridge',
		city='Naperville',
		state='IL',
		postal_code='60540',
		country='USA'
	))
	db.session.commit()

	# Assign as lead of Infrastructure Team
	teams[3].lead_id = it_manager.id
	db.session.commit()



	### --- HR EMPLOYEE ---
	hr_emp = Employee(
		first_name='Linda',
		last_name='Perez',
		email='linda.hr@teammanager.com',
		phone='555-1010',
		position='HR Specialist',
		role=Role.EMPLOYEE,
		hire_date=date.today(),
		department_id=hr_dept.id
	)
	db.session.add(hr_emp)
	db.session.commit()

	db.session.add(Address(
		employee_id=hr_emp.id,
		type='Home',
		street='12 Willow Street',
		city='Bolingbrook',
		state='IL',
		postal_code='60440',
		country='USA'
	))
	db.session.commit()



	### --- IT SUPPORT EMPLOYEE ---
	it_emp = Employee(
		first_name='Michael',
		last_name='Green',
		email='michael.it@teammanager.com',
		phone='555-2010',
		position='IT Support Specialist',
		role=Role.EMPLOYEE,
		hire_date=date.today(),
		department_id=it_dept.id
	)
	db.session.add(it_emp)
	db.session.commit()

	db.session.add(Address(
		employee_id=it_emp.id,
		type='Home',
		street='8 Ridgeview Drive',
		city='Chicago',
		state='IL',
		postal_code='60616',
		country='USA'
	))
	db.session.commit()



	### --- SALES EMPLOYEE ---
	sales_emp = Employee(
		first_name='Kevin',
		last_name='Roberts',
		email='kevin.sales@teammanager.com',
		phone='555-3005',
		position='Sales Representative',
		role=Role.EMPLOYEE,
		hire_date=date.today(),
		department_id=sales_dept.id
	)
	db.session.add(sales_emp)
	db.session.commit()

	db.session.add(Address(
		employee_id=sales_emp.id,
		type='Home',
		street='200 Lakeview Pkwy',
		city='Schaumburg',
		state='IL',
		postal_code='60173',
		country='USA'
	))
	db.session.commit()



	### --- FINANCE EMPLOYEE ---
	finance_emp = Employee(
		first_name='Hannah',
		last_name='Williams',
		email='hannah.finance@teammanager.com',
		phone='555-4005',
		position='Accountant',
		role=Role.EMPLOYEE,
		hire_date=date.today(),
		department_id=finance_dept.id
	)
	db.session.add(finance_emp)
	db.session.commit()

	db.session.add(Address(
		employee_id=finance_emp.id,
		type='Home',
		street='333 Brookside Ave',
		city='Wheaton',
		state='IL',
		postal_code='60187',
		country='USA'
	))
	db.session.commit()



	# ------------------------------------------------------------------------------------
	# ---------------------------------- USERS -------------------------------------------
	# ------------------------------------------------------------------------------------

	def create_user(username, email, employee_id):
		u = User(username=username, email=email, employee_id=employee_id)
		u.set_password("password123")
		return u

	users = [
		create_user('sarah_hr', 'sarah.hr@teammanager.com', hr_manager.id),
		create_user('james_it', 'james.it@teammanager.com', it_manager.id),
		create_user('linda_hr', 'linda.hr@teammanager.com', hr_emp.id),
		create_user('michael_it', 'michael.it@teammanager.com', it_emp.id),
		create_user('kevin_sales', 'kevin.sales@teammanager.com', sales_emp.id),
		create_user('hannah_finance', 'hannah.finance@teammanager.com', finance_emp.id),
	]

	db.session.add_all(users)
	db.session.commit()

	print("All sample departments, teams, employees, addresses, and users created successfully!")

	# ------------------------------------------------------------------------------------
	# ---------------------------------- TASKS -------------------------------------------
	# ------------------------------------------------------------------------------------

	# Fetch all created users for clarity
	admin_user = User.query.filter_by(username='admin').first()
	sarah_user = User.query.filter_by(username='sarah_hr').first()
	james_user = User.query.filter_by(username='james_it').first()
	linda_user = User.query.filter_by(username='linda_hr').first()
	michael_user = User.query.filter_by(username='michael_it').first()
	kevin_user = User.query.filter_by(username='kevin_sales').first()
	hannah_user = User.query.filter_by(username='hannah_finance').first()

	now = datetime.now(timezone.utc)

	tasks = [

		# Admin-created tasks
		Task(
			title="System Security Audit",
			description="Perform a full security audit of infrastructure and systems.",
			status="in_progress",
			priority="high",
			assigned_to_id=james_user.id,
			created_by_id=admin_user.id,
			due_date=now + timedelta(days=7),
		),

		Task(
			title="Prepare Quarterly HR Report",
			description="Compile HR data for the upcoming quarterly presentation.",
			status="pending",
			priority="medium",
			assigned_to_id=sarah_user.id,
			created_by_id=admin_user.id,
			due_date=now + timedelta(days=10),
		),

		Task(
			title="Server Backup Verification",
			description="Verify all automated backups are functioning correctly.",
			status="pending",
			priority="high",
			assigned_to_id=michael_user.id,
			created_by_id=admin_user.id,
			due_date=now + timedelta(days=3),
		),

		# HR Manager created tasks
		Task(
			title="New Employee Onboarding",
			description="Handle onboarding process for 3 new hires.",
			status="in_progress",
			priority="medium",
			assigned_to_id=linda_user.id,
			created_by_id=sarah_user.id,
			due_date=now + timedelta(days=5),
		),

		Task(
			title="Policy Review Meeting",
			description="Schedule and conduct a meeting to review company internal policies.",
			status="pending",
			priority="low",
			assigned_to_id=sarah_user.id,
			created_by_id=sarah_user.id,
			due_date=now + timedelta(days=14),
		),

		# IT Manager created tasks
		Task(
			title="Network Infrastructure Upgrade",
			description="Upgrade the company's network switches and firewalls.",
			status="pending",
			priority="high",
			assigned_to_id=michael_user.id,
			created_by_id=james_user.id,
			due_date=now + timedelta(days=21),
		),

		# Sales task
		Task(
			title="Client Outreach Campaign",
			description="Reach out to 25 new corporate clients.",
			status="in_progress",
			priority="medium",
			assigned_to_id=kevin_user.id,
			created_by_id=admin_user.id,
			due_date=now + timedelta(days=12),
		),

		# Finance task
		Task(
			title="Prepare Monthly Financial Statement",
			description="Complete and submit the monthly finance statement.",
			status="completed",
			priority="high",
			assigned_to_id=hannah_user.id,
			created_by_id=admin_user.id,
			due_date=now - timedelta(days=2),
			completed_at=now - timedelta(days=1),
		),

		Task(
			title="Budget Forecast for Q2",
			description="Prepare the Q2 budget forecast and send it for review.",
			status="pending",
			priority="high",
			assigned_to_id=hannah_user.id,
			created_by_id=james_user.id,
			due_date=now + timedelta(days=30),
		),

		# Small IT task
		Task(
			title="Helpdesk Ticket Cleanup",
			description="Close or update outdated helpdesk tickets.",
			status="pending",
			priority="low",
			assigned_to_id=michael_user.id,
			created_by_id=james_user.id,
			due_date=now + timedelta(days=4),
		),
	]

	db.session.add_all(tasks)
	db.session.commit()

	print("Sample tasks have been created successfully!")

