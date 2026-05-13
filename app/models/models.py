"""
ORM models — adapted from the desktop EMS for Flask-SQLAlchemy.
All table schemas are preserved; the Base now comes from db.Model.
"""
from datetime import datetime, date
import enum

from flask_login import UserMixin
from app.extensions import db


# ─── Enumerations ─────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    ADMIN    = "admin"
    EMPLOYEE = "employee"


class EmployeeStatus(str, enum.Enum):
    ACTIVE     = "active"
    INACTIVE   = "inactive"
    TERMINATED = "terminated"


class AttendanceStatus(str, enum.Enum):
    PRESENT  = "present"
    ABSENT   = "absent"
    LATE     = "late"
    HALF_DAY = "half_day"


class LeaveStatus(str, enum.Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveType(str, enum.Enum):
    ANNUAL    = "annual"
    SICK      = "sick"
    MATERNITY = "maternity"
    UNPAID    = "unpaid"
    OTHER     = "other"


# ─── Models ───────────────────────────────────────────────────────────────────

class Department(db.Model):
    __tablename__ = "departments"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    employees = db.relationship("Employee", back_populates="department", lazy="select")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Employee(db.Model):
    __tablename__ = "employees"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    emp_code      = db.Column(db.String(20), unique=True, nullable=False)
    first_name    = db.Column(db.String(50), nullable=False)
    last_name     = db.Column(db.String(50), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    phone         = db.Column(db.String(20), default="")
    hire_date     = db.Column(db.Date, default=date.today)
    salary        = db.Column(db.Float, default=0.0)
    position      = db.Column(db.String(100), default="")
    status        = db.Column(db.String(20), default=EmployeeStatus.ACTIVE.value)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department   = db.relationship("Department", back_populates="employees")
    user         = db.relationship("User", back_populates="employee", uselist=False)
    attendance   = db.relationship("Attendance", back_populates="employee",
                                    cascade="all, delete-orphan")
    leaves       = db.relationship("Leave", back_populates="employee",
                                    cascade="all, delete-orphan",
                                    foreign_keys="Leave.employee_id")
    payrolls     = db.relationship("Payroll", back_populates="employee",
                                    cascade="all, delete-orphan")
    performances = db.relationship("Performance", back_populates="employee",
                                    cascade="all, delete-orphan",
                                    foreign_keys="Performance.employee_id")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.full_name}')>"


class User(UserMixin, db.Model):
    """Flask-Login compatible user model."""
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role          = db.Column(db.String(20), default=UserRole.EMPLOYEE.value)
    employee_id   = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    is_active     = db.Column(db.Boolean, default=True)
    last_login    = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="user")

    # Flask-Login uses `is_active` as a column — override the property
    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Attendance(db.Model):
    __tablename__ = "attendance"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    date        = db.Column(db.Date, nullable=False, default=date.today)
    check_in    = db.Column(db.String(10), default="")   # HH:MM
    check_out   = db.Column(db.String(10), default="")   # HH:MM
    status      = db.Column(db.String(20), default=AttendanceStatus.PRESENT.value)
    notes       = db.Column(db.Text, default="")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="attendance")

    def __repr__(self):
        return f"<Attendance(emp={self.employee_id}, date={self.date}, status='{self.status}')>"


class Leave(db.Model):
    __tablename__ = "leaves"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    leave_type  = db.Column(db.String(20), default=LeaveType.ANNUAL.value)
    start_date  = db.Column(db.Date, nullable=False)
    end_date    = db.Column(db.Date, nullable=False)
    reason      = db.Column(db.Text, default="")
    status      = db.Column(db.String(20), default=LeaveStatus.PENDING.value)
    approved_by = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="leaves",
                                foreign_keys=[employee_id])
    approver = db.relationship("Employee", foreign_keys=[approved_by])

    @property
    def duration_days(self) -> int:
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __repr__(self):
        return f"<Leave(emp={self.employee_id}, type='{self.leave_type}', status='{self.status}')>"


class Payroll(db.Model):
    __tablename__ = "payroll"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id  = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    month        = db.Column(db.Integer, nullable=False)   # 1-12
    year         = db.Column(db.Integer, nullable=False)
    base_salary  = db.Column(db.Float, default=0.0)
    allowances   = db.Column(db.Float, default=0.0)
    deductions   = db.Column(db.Float, default=0.0)
    net_pay      = db.Column(db.Float, default=0.0)
    working_days = db.Column(db.Integer, default=0)
    present_days = db.Column(db.Integer, default=0)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="payrolls")

    def __repr__(self):
        return f"<Payroll(emp={self.employee_id}, {self.month}/{self.year}, net={self.net_pay})>"


class Performance(db.Model):
    __tablename__ = "performance"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    rating      = db.Column(db.Integer, default=3)   # 1-5
    comments    = db.Column(db.Text, default="")
    review_date = db.Column(db.Date, default=date.today)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", back_populates="performances",
                                foreign_keys=[employee_id])
    reviewer = db.relationship("Employee", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<Performance(emp={self.employee_id}, rating={self.rating})>"
