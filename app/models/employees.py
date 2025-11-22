from datetime import datetime, timezone
from enum import Enum
from app import db

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    
class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    position = db.Column(db.String(100))
    role = db.Column(db.Enum(Role), default=Role.EMPLOYEE, nullable=False)
    hire_date = db.Column(db.Date)
    salary = db.Column(db.Float)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', back_populates='employee', uselist=False)
    addresses = db.relationship('Address', backref='employee', lazy=True)
    department = db.relationship('Department', back_populates='employees')
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Employee id={self.id} name={self.full_name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value if self.role else None,
            "department": self.department.name if self.department else None,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "salary": self.salary,
            "manager_id": self.manager_id,
            "addresses": [addr.to_dict() for addr in self.addresses],
        }
