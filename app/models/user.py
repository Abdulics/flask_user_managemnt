from datetime import datetime, timezone
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app.models.employees import Role

class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class User(UserMixin, db.Model, TimestampMixin):
    """
    Base user model for user/teams manager.
    - Designed for use with Flask-SQLAlchemy (db.Model).
    - Includes password hashing helpers, basic flags, metadata JSON and team relationship.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))

    # store hashed password (protected attribute name)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    bio = db.Column(db.Text, nullable=True)
    user_metadata = db.Column(db.JSON, nullable=False, default=dict)  # free-form user metadata
    last_login = db.Column(db.DateTime, nullable=True)

    employee = db.relationship('Employee', back_populates='user')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', back_populates='recipient', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to_id', back_populates='assigned_to', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by_id', back_populates='created_by', lazy='dynamic')

    # relationship to Attendance model
    attendances = db.relationship( "Attendance", back_populates="user", lazy="dynamic")

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
        self.last_login = datetime.now(datetime.timezone.utc)

    @property
    def role(self) -> Optional[Role]:
        """Return the employee role, if linked."""
        return self.employee.role if self.employee else None

    @property
    def role_name(self) -> Optional[str]:
        """Lowercase role name for quick comparisons."""
        return self.role.value.lower() if self.role else None

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_employee(self) -> bool:
        return self.role == Role.EMPLOYEE

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
