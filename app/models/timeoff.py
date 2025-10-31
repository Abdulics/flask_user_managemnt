from datetime import datetime, date, timezone
import enum
from app import db
from sqlalchemy.orm import validates

class TimeOffType(enum.Enum):
    VACATION = "vacation"
    SICK = "sick"
    UNPAID = "unpaid"
    OTHER = "other"


class TimeOffStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"

class TimestampMixin:
    """Reusable timestamp fields."""
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

class TimeOff(db.Model, TimestampMixin):
    __tablename__ = "timeoffs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    type = db.Column(db.Enum(TimeOffType), nullable=False, default=TimeOffType.VACATION)
    status = db.Column(db.Enum(TimeOffStatus), nullable=False, default=TimeOffStatus.PENDING)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    reason = db.Column(db.Text, nullable=True)

    # relationship: assumes a User model exists with __tablename__ == "user"
    user = db.relationship("User", backref=db.backref("timeoffs", lazy="dynamic"))

    def __repr__(self):
        return f"<TimeOff id={self.id} user_id={self.user_id} {self.start_date}→{self.end_date} status={self.status.value}>"

    @property
    def duration_days(self) -> int:
        """Inclusive number of days for the time off."""
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days + 1

    def approve(self):
        self.status = TimeOffStatus.APPROVED

    def deny(self):
        self.status = TimeOffStatus.DENIED

    def cancel(self):
        self.status = TimeOffStatus.CANCELLED

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "start_date": self.start_date.isoformat() if isinstance(self.start_date, date) else None,
            "end_date": self.end_date.isoformat() if isinstance(self.end_date, date) else None,
            "reason": self.reason,
            "duration_days": self.duration_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @validates("end_date", "start_date")
    def _validate_dates(self, key, value):
        if not isinstance(value, date):
            raise ValueError(f"{key} must be a date")
        # If both dates present, ensure end >= start
        other = self.start_date if key == "end_date" else self.end_date
        if other is not None and isinstance(other, date) and key == "end_date" and value < other:
            raise ValueError("end_date must be on or after start_date")
        if other is not None and isinstance(other, date) and key == "start_date" and value > other:
            raise ValueError("start_date must be on or before end_date")
        return value

    def overlaps(self, other_start: date, other_end: date) -> bool:
        """Return True if this timeoff overlaps the given date range (inclusive)."""
        if not (self.start_date and self.end_date and other_start and other_end):
            return False
        return not (self.end_date < other_start or self.start_date > other_end)