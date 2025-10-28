from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey, DateTime

# app/models/paystub.py
# Paystub SQLAlchemy model compatible with Flask-SQLAlchemy when `db` is available,
# and falls back to plain SQLAlchemy declarative base otherwise.


# Try to use existing Flask-SQLAlchemy `db` if the app provides it; otherwise use plain SQLAlchemy.
try:
    from app import db  # typical project layout: app/__init__.py exposes db = SQLAlchemy()
    Column = db.Column
    Integer = db.Integer
    String = db.String
    Date = db.Date
    Numeric = db.Numeric
    Text = db.Text
    ForeignKey = db.ForeignKey
    DateTime = db.DateTime
    ModelBase = db.Model
except Exception:
    ModelBase = declarative_base()


class Paystub(ModelBase):
    __tablename__ = "paystubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Link to a user/employee record; adjust foreign key target to match your users table
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)

    gross_pay = Column(Numeric(12, 2), nullable=False, default=0)
    taxes = Column(Numeric(12, 2), nullable=False, default=0)
    deductions = Column(Numeric(12, 2), nullable=False, default=0)
    net_pay = Column(Numeric(12, 2), nullable=False, default=0)

    # Optional storage reference to original file (PDF, image) or external storage key
    file_path = Column(String(1024), nullable=True)
    notes = Column(Text, nullable=True)

    issued_at = Column(DateTime, nullable=True, default=datetime.now(datetime.timezone.utc))
    created_at = Column(DateTime, nullable=False, default=datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc))

    def __repr__(self) -> str:
        return f"<Paystub id={self.id} employee_id={self.employee_id} period={self.pay_period_start}→{self.pay_period_end} net={self.net_pay}>"

    # Utility: safe Decimal conversion for monetary values
    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if value is None or value == "":
            return Decimal("0.00")
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid monetary amount: {value}")

    def calculate_net_pay(self) -> Decimal:
        """
        Recompute net_pay from gross_pay, taxes and deductions.
        Returns the computed net as Decimal and updates the model field.
        """
        gross = self._to_decimal(self.gross_pay)
        taxes = self._to_decimal(self.taxes)
        deductions = self._to_decimal(self.deductions)
        net = gross - taxes - deductions
        # ensure two decimal places
        net = net.quantize(Decimal("0.01"))
        self.net_pay = net
        return net

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update fields from a dict (typically from request.json).
        Accepts keys: pay_period_start/pay_period_end (date or ISO string),
        gross_pay, taxes, deductions, file_path, notes, issued_at.
        """
        if "pay_period_start" in data:
            v = data["pay_period_start"]
            self.pay_period_start = v if isinstance(v, date) else date.fromisoformat(v)
        if "pay_period_end" in data:
            v = data["pay_period_end"]
            self.pay_period_end = v if isinstance(v, date) else date.fromisoformat(v)

        for money_field in ("gross_pay", "taxes", "deductions", "net_pay"):
            if money_field in data:
                setattr(self, money_field, self._to_decimal(data[money_field]))

        if "file_path" in data:
            self.file_path = data.get("file_path")
        if "notes" in data:
            self.notes = data.get("notes")
        if "issued_at" in data:
            v = data["issued_at"]
            self.issued_at = v if isinstance(v, datetime) else datetime.fromisoformat(v)

        # After updating monetary fields, ensure net_pay is consistent
        self.calculate_net_pay()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the paystub to a JSON-serializable dict.
        Decimal values are rendered as strings to preserve precision.
        """
        def dec(v):
            return format(v, "0.2f") if v is not None else None

        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "pay_period_start": self.pay_period_start.isoformat() if self.pay_period_start else None,
            "pay_period_end": self.pay_period_end.isoformat() if self.pay_period_end else None,
            "gross_pay": dec(self.gross_pay),
            "taxes": dec(self.taxes),
            "deductions": dec(self.deductions),
            "net_pay": dec(self.net_pay),
            "file_path": self.file_path,
            "notes": self.notes,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def validate_dates(self) -> None:
        """
        Basic validation: pay_period_start must be <= pay_period_end.
        Call before saving to DB if necessary.
        """
        if self.pay_period_start and self.pay_period_end and self.pay_period_start > self.pay_period_end:
            raise ValueError("pay_period_start must be before or equal to pay_period_end")