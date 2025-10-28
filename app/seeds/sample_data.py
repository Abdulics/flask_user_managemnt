from datetime import datetime
from typing import Optional, Dict, Any

from app import db
from app.models.user import User


def create_full_user(
	username: str = "jdoe",
	email: str = "jdoe@example.com",
	password: str = "Password123!",
	is_admin: bool = True,
	is_active: bool = True,
	bio: Optional[str] = "A sample full-featured user created by seed.",
	user_metadata: Optional[Dict[str, Any]] = None,
	last_login: Optional[datetime] = None,
	commit: bool = False,
	app=None,
) -> User:
	"""Create and return a fully populated User instance.

	This helper builds a User object with sensible defaults and sets the
	password hash. If `commit=True` and an application `app` is provided,
	the user will be added to the database and committed inside an
	application context.

	Returns the User instance (committed or not depending on arguments).
	"""

	if user_metadata is None:
		user_metadata = {
			"preferences": {"theme": "dark", "notifications": True},
			"tags": ["sample", "seed"],
		}

	user = User(username=username, email=email)
	user.is_admin = is_admin
	user.is_active = is_active
	user.bio = bio
	user.user_metadata = user_metadata
	# set explicit last_login if provided
	if last_login:
		user.last_login = last_login
	else:
		# leave as None or set to now for demonstration
		user.last_login = datetime.now(datetime.timezone.utc)

	# set password (writes hashed password)
	user.set_password(password)

	# Optionally persist to DB when an app context is provided
	if commit:
		if app is None:
			raise RuntimeError("To commit to the database, pass a Flask `app` instance.")
		with app.app_context():
			db.session.add(user)
			db.session.commit()

	return user


if __name__ == "__main__":
	# Basic demonstration (won't commit unless you provide a create_app / app)
	demo = create_full_user()
	print("Created user object (not persisted):", demo)
