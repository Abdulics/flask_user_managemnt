from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# /workspaces/flask_user_managemnt/app/models/user.py


# association table for many-to-many User <-> Team
team_members = db.Table(
    "team_members",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("team_id", db.Integer, db.ForeignKey("team.id"), primary_key=True),
)


class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(datetime.timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))


class User(db.Model, TimestampMixin):
    """
    Base user model for user/teams manager.
    - Designed for use with Flask-SQLAlchemy (db.Model).
    - Includes password hashing helpers, basic flags, metadata JSON and team relationship.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # store hashed password (protected attribute name)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    bio = db.Column(db.Text, nullable=True)
    user_metadata = db.Column(db.JSON, nullable=False, default=dict)  # free-form user metadata
    last_login = db.Column(db.DateTime, nullable=True)

    # relationship to Team model (define Team in another module). 'members' backref on Team.
    teams = db.relationship(
        "Team",
        secondary=team_members,
        backref=db.backref("members", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"

    # password property: write-only
    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, raw: str) -> None:
        self.set_password(raw)

    def set_password(self, raw: str) -> None:
        """Hash and set the user's password."""
        self._password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        """Check a plaintext password against the stored hash."""
        if not self._password_hash:
            return False
        return check_password_hash(self._password_hash, raw)

    def touch_last_login(self) -> None:
        """Set last_login to now (useful after successful auth)."""
        self.last_login = datetime.now(datetime.timezone.utc)()

    def to_dict(self, include_email: bool = False) -> Dict[str, Any]:
        """Serialize user to dict. Avoid exposing sensitive fields by default."""
        data = {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "bio": self.bio,
            "user_metadata": self.user_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        if include_email:
            data["email"] = self.email
        return data

    def from_dict(self, data: Dict[str, Any], set_password: bool = False) -> None:
        """
        Update fields from a dict. If set_password is True and 'password' in data,
        it will be hashed and set.
        """
        for field in ("username", "email", "bio"):
            if field in data:
                setattr(self, field, data[field])
        if "metadata" in data:
            self.metadata = data["metadata"]
        if set_password and "password" in data:
            self.password = data["password"]

    # convenience helpers for team membership
    def add_to_team(self, team) -> None:
        if team not in self.teams:
            self.teams.append(team)

    def remove_from_team(self, team) -> None:
        self.teams.remove(team)