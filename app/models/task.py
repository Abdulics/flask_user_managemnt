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
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime, nullable=True, default=None)
    
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], back_populates='assigned_tasks')
    created_by = db.relationship('User', foreign_keys=[created_by_id], back_populates='created_tasks')

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"

    
