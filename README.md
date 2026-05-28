# Team Manager (Work in Progress)

A Flask-based internal operations system for small teams/companies. Core features: role-based dashboards (Admin/Manager/Employee), employee/user management, tasks, attendance, time tracking (clock in/out), time-off requests with manager -> HR workflow, messaging, and paystubs.

> Status: actively evolving. Expect breaking changes; run migrations after pulls.

## Stack
- Python 3.x, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- PostgreSQL (configure via `.env`)

## Setup
1) Create a virtualenv and install dependencies:
```bash
pip install -r requirements.txt
```
2) Configure environment in `.env` (example):
```
SECRET_KEY=change-me
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=team_manager
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_DEFAULT_SENDER=no-reply@example.com
```
3) Initialize/migrate the database (PostgreSQL):
```bash
flask db upgrade
```
4) Seed default admin (must) and sample data (optional):
```bash
flask init-db        # creates admin: admin/admin123
python app/seeds/sample_data.py
```
5) Run the app:
```bash
flask run
```

## Demo Accounts
Default admin:
```text
admin / admin123
```

Seeded demo users:
```text
sarah_hr / password123
james_it / password123
linda_hr / password123
michael_it / password123
kevin_sales / password123
hannah_finance / password123
```

## Reset Local Demo Database
This clears the PostgreSQL public schema, rebuilds migrations, recreates the default admin, and reloads demo data:
```bash
python -c "from app import create_app, db; from sqlalchemy import text; app=create_app(); app.app_context().push(); db.session.execute(text('DROP SCHEMA IF EXISTS public CASCADE')); db.session.execute(text('CREATE SCHEMA public')); db.session.execute(text('GRANT ALL ON SCHEMA public TO public')); db.session.commit()"
flask db upgrade
flask init-db
python app/seeds/sample_data.py
```

## Tests
Run the automated flow checks:
```bash
pytest
```

The tests use a temporary SQLite database and do not touch your PostgreSQL demo database.

## Features
- **Auth & Roles**: Admin, Manager, Employee (role stored on Employee; users link to employees).
- **Change Password**: Authenticated users can update their own password from the user menu.
- **User/Employee Management**: Admin creates employees (must assign a manager), users self-register to link to their employee.
- **Teams**: Admins, managers, and HR can manage team structure; employees are assigned into teams.
- **Tasks**: Admins assign tasks broadly; managers assign tasks to their own team members; employees manage their own tasks.
- **Attendance**: Employees mark daily status; managers/admins/HR can view team attendance.
- **Time Tracking**: Clock in/out with live timers in navbar and dashboards; personal time log.
- **Time Off**: Employee submits -> Manager approves/denies -> HR approves/denies; HR queue for manager-approved requests; notifications via internal messages.
- **Messaging**: Internal inbox/sent/compose/reply.
- **Paystubs**: Admin creates paystubs; employees view their own.

## Key Routes
- `/auth/login`, `/auth/register`
- `/dashboard` (redirects by role)
- `/tasks`, `/tasks/create`
- `/attendance`, `/attendance/team`
- `/time-tracker/log`, `/time-tracker/clock-in`, `/time-tracker/clock-out`
- `/timeoff` (self), `/timeoff/team` (manager/admin), `/timeoff/hr` (HR/admin)
- `/paystubs`, `/paystubs/create`
- `/messages`, `/messages/compose`

## Data Model Notes
- Role is on `Employee` (Role enum). `User` exposes helpers (`is_admin`, etc.) derived from the linked employee.
- Time off now includes manager/HR decision fields and statuses (`pending`, `manager_approved`, `approved`, `denied`, `cancelled`).
- Time tracking uses `time_entries` for clock in/out sessions.

## Migrations
After model changes, run:
```bash
flask db migrate -m "describe change"
flask db upgrade
```

## Work in Progress
- More validation, notifications, and UI polish are planned.
- Review schema and flows after pulling updates; re-run migrations.

