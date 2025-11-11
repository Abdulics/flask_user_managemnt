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

    def validate_dates(self) -> None:
        """
        Basic validation: pay_period_start must be <= pay_period_end.
        Call before saving to DB if necessary.
        """
        if self.pay_period_start and self.pay_period_end and self.pay_period_start > self.pay_period_end:
            raise ValueError("pay_period_start must be before or equal to pay_period_end")