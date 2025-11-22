<!-- Copied and tailored for this repository. Keep concise, actionable, and specific. -->
# Copilot / AI Agent Instructions for Team Manager

This file gives concise, repository-specific guidance so an AI coding assistant can be productive immediately.

## Project Big Picture
- **What it is:** A Flask-based internal user management app (tasks, attendance, time-off, messaging, paystubs).
- **Entry points:** `run.py` (calls `create_app()`), `app/__init__.py` (application factory and CLI), and Flask CLI (`flask` commands).
- **Data layer:** SQLAlchemy models live in `app/models/` and migrations are managed with Flask-Migrate / Alembic (`migrations/`).
- **Routing:** Routes are organized as Blueprints in `app/routes/` (e.g. `auth.py`, `dashboard.py`, `admin.py`). Registering happens in `create_app()`.
- **Forms & templates:** WTForms in `app/forms/`, templates in `app/templates/` with subfolders (`auth/`, `dashboard/`, `admin/`, etc.).

## Key Files to Reference
- `app/__init__.py` — application factory, CLI command `init-db`, blueprint registration, error handlers, `login_manager` configuration.
- `run.py` — simple runner that instantiates the app and enables migrations.
- `config.py` — environment-driven config (uses `.env`). Important env vars: `SECRET_KEY`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `MAIL_*`.
- `app/models/` — domain models (user, employees, department, task, message, etc.).
- `app/routes/` — blueprint handlers and view logic; follow existing naming and registration.
- `app/forms/` — form classes used across views (search here for validation patterns and field names).
- `app/seeds/sample_data.py` — example seed data. `flask init-db` creates an admin user; use seeds for richer dev data.
- `requirements.txt` — dependency pinning. Use `pip install -r requirements.txt` to replicate dev environment.

## Developer Workflows & Commands
- Install: `pip install -r requirements.txt`.
- Run locally: either `python run.py` or set `FLASK_APP=run.py` then `flask run` (Windows PowerShell: `setx FLASK_APP run.py` then open new shell).
- Migrations (as in `README.md`):
  - `flask db init` (once)
  - `flask db migrate -m "message"`
  - `flask db upgrade`
- Seed DB: `flask init-db` (custom CLI command defined in `app/__init__.py` — it creates a default admin user). For larger seeds, run `app/seeds/sample_data.py` directly or import its helper functions under an app context.
- Tests: run `pytest -q` from repo root (tests present in `tests/`).

## Project-specific Conventions & Patterns
- Blueprints are registered explicitly in `create_app()`; when adding a new route file, import and register it there.
- Models are imported in `create_app()` to ensure Alembic detects them (`from app.models import ...`). Add new model modules to that import list when needed.
- Authentication uses `flask-login`. The login view is `auth.login` (see `login_manager.login_view = "auth.login"`). Use `current_user` and `@login_required` accordingly.
- CSRF protection: `CSRFProtect(app)` is applied globally — forms must include CSRF tokens (templates provided follow this pattern).
- Config is environment-driven; do not hardcode secrets. `config.py` constructs the Postgres URI from env vars — tests or CI may need a separate SQLite/CI config.

## Integration Points & External Dependencies
- Database: Postgres via SQLAlchemy (set via `SQLALCHEMY_DATABASE_URI`). Ensure DB credentials in `.env` for local dev.
- Email: optional, configured via `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`.
- Migrations: `flask-migrate` / Alembic — migrations are in `migrations/`.

## Safe Editing Practices for AI Agents
- When adding models: update `app/models/` file and add the module name to the `from app.models import ...` import in `create_app()` so Alembic picks it up.
- When adding new blueprints: create file in `app/routes/`, expose `*_bp` blueprint, and register it in `create_app()` in `app/__init__.py`.
- Avoid changing `create_app()` behavior unless necessary; keep registration explicit and grouped.
- Do not leave `debug=True` or stray `print()` calls in `config.py`/`run.py` for production. There is a `print('basedir:', basedir)` in `config.py` that is likely debug-only.

## Small Examples (copyable)
- Run dev server quickly:
  - PowerShell:
    - `pip install -r requirements.txt`
    - `setx FLASK_APP run.py ; flask run`
- Create and migrate DB:
  - `flask db migrate -m "add XYZ" ; flask db upgrade`
- Create admin user (first-run):
  - `flask init-db`

## Where to Look for Patterns
- Authorization and manager/employee boundaries: `app/routes/manager.py`, `app/routes/admin.py`, and `app/models/employees.py`.
- Messaging flow: `app/models/message.py` + `app/routes/messages.py` + templates in `templates/messages/`.
- Task lifecycle: `app/models/task.py` + `app/routes/tasks.py` + `templates/tasks/`.

If any section is unclear or you'd like me to expand examples (e.g., how to run seeds, run tests in CI, or add a new model + migration), tell me which area to expand and I will iterate.
