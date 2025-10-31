from datetime import datetime, timezone
from typing import Dict, Any
from app import db

class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
class Task(db.Model, TimestampMixin):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True, default="")
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)
    due_date = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    user = db.relationship("User", back_populates="tasks", lazy="joined")

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} completed={self.completed}>"

    def to_dict(self) -> Dict[str, Any]:
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
        for field in ("title", "description", "completed", "priority", "due_date"):
            if field in data:
                setattr(self, field, data[field])

    def mark_completed(self):
        self.completed = True

    def assign_to(self, user):
        if user is None:
            self.user = None
            self.user_id = None
        else:
            assert hasattr(user, "id"), "assign_to expects a User instance"
            self.user = user
