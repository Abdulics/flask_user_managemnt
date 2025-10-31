from datetime import datetime
from app import db
from app.models.user import User

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    salary = db.Column(db.Float)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))

    # Relationships
    user = db.relationship('User', backref=db.backref('employee', uselist=False))
    manager = db.relationship('Employee', remote_side=[id], backref='subordinates')
    addresses = db.relationship('Address', backref='employee', lazy=True)  # link to Address table

    def __init__(self, user_id, employee_id, first_name, last_name, department=None, position=None, salary=None, manager_id=None):
        self.user_id = user_id
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.position = position
        self.salary = salary
        self.manager_id = manager_id

    def __repr__(self):
        return f'<Employee {self.employee_id} - {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'salary': self.salary,
            'manager_id': self.manager_id,
            'addresses': [addr.to_dict() for addr in self.addresses]  # optional: include addresses
        }
