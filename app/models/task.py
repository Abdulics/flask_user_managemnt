from datetime import datetime
from typing import Optional, Dict, Any

from app import db  # assumes `db = SQLAlchemy()` is created in app package


class Task(db.Model):
    """
    Task model representing a single task assigned (optionally) to a user.
    Fields:
      - id: primary key
      - title: short title (required)
      - description: optional detailed notes
      - completed: boolean flag
      - priority: integer priority (higher = more important)
      - due_date: optional deadline
      - created_at / updated_at: timestamps
      - user_id: FK to users.id (nullable)
    """
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, default="", nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    priority = db.Column(db.Integer, nullable=False, default=0)
    due_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user = db.relationship("User", back_populates="tasks", lazy="joined")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} completed={self.completed}>"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to a plain dict suitable for JSON responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update allowed fields from a dict and touch updated_at via SQLAlchemy onupdate."""
        for field in ("title", "description", "completed", "priority", "due_date", "user_id"):
            if field in data:
                setattr(self, field, data[field])

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.completed = True

    def assign_to(self, user) -> None:
        """Assign task to a user instance (or set user_id)."""
        if user is None:
            self.user_id = None
            self.user = None
        else:
            # accept either a user instance or an integer id
            self.user = user if hasattr(user, "id") else None
            self.user_id = getattr(user, "id", user)

# Ensure a reciprocal relationship exists on the User model:
# In app/models/user.py:
# tasks = db.relationship("Task", back_populates="user", cascade="all, delete-orphan")