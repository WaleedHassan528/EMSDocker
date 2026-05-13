"""
Employee CRUD service — adapted for Flask-SQLAlchemy.
All business logic is preserved from the original desktop EMS.
"""
from datetime import date

from app.extensions import db
from app.models.models import Employee, Department, EmployeeStatus
from app.utils.validators import (
    validate_name, validate_email, validate_phone,
    validate_salary, validate_date,
)
from app.utils.helpers import generate_emp_code, parse_date


class EmployeeService:

    @staticmethod
    def get_all(status_filter: str | None = None) -> list[dict]:
        """Return all employees as a list of dicts, optionally filtered by status."""
        q = Employee.query
        if status_filter:
            q = q.filter_by(status=status_filter)
        employees = q.order_by(Employee.first_name).all()
        return [EmployeeService._to_dict(e) for e in employees]

    @staticmethod
    def get_by_id(emp_id: int) -> dict | None:
        e = db.session.get(Employee, emp_id)
        return EmployeeService._to_dict(e) if e else None

    @staticmethod
    def get_obj_by_id(emp_id: int) -> Employee | None:
        """Return the ORM object directly (for internal service use)."""
        return db.session.get(Employee, emp_id)

    @staticmethod
    def get_by_emp_code(emp_code: str) -> dict | None:
        e = Employee.query.filter_by(emp_code=emp_code.upper()).first()
        return EmployeeService._to_dict(e) if e else None

    @staticmethod
    def search(query: str) -> list[dict]:
        """Search employees by name, email, or emp_code."""
        q_lower = f"%{query.lower()}%"
        employees = Employee.query.filter(
            (Employee.first_name.ilike(q_lower)) |
            (Employee.last_name.ilike(q_lower))  |
            (Employee.email.ilike(q_lower))       |
            (Employee.emp_code.ilike(q_lower))
        ).all()
        return [EmployeeService._to_dict(e) for e in employees]

    @staticmethod
    def create(data: dict) -> tuple[bool, str]:
        """Create a new employee. Returns (success, message|new_id)."""
        errors = EmployeeService._validate(data)
        if errors:
            return False, "\n".join(errors)

        # Check unique email
        if Employee.query.filter_by(email=data["email"].strip().lower()).first():
            return False, f"Email '{data['email']}' is already registered."

        # Auto-generate or validate emp_code
        emp_code = data.get("emp_code", "").strip().upper()
        if not emp_code:
            existing_codes = [e.emp_code for e in Employee.query.all()]
            emp_code = generate_emp_code(existing_codes)
        else:
            if Employee.query.filter_by(emp_code=emp_code).first():
                return False, f"Employee code '{emp_code}' already exists."

        # Validate department
        dept_id = data.get("department_id")
        if dept_id:
            dept = db.session.get(Department, int(dept_id))
            if not dept:
                return False, "Selected department not found."

        hire_date = parse_date(data.get("hire_date", "")) or date.today()

        emp = Employee(
            emp_code=emp_code,
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
            email=data["email"].strip().lower(),
            phone=data.get("phone", "").strip(),
            salary=float(data.get("salary", 0)),
            position=data.get("position", "").strip(),
            department_id=int(dept_id) if dept_id else None,
            hire_date=hire_date,
            status=data.get("status", EmployeeStatus.ACTIVE.value),
        )
        db.session.add(emp)
        db.session.commit()
        return True, str(emp.id)

    @staticmethod
    def update(emp_id: int, data: dict) -> tuple[bool, str]:
        """Update an existing employee's details."""
        errors = EmployeeService._validate(data, is_update=True)
        if errors:
            return False, "\n".join(errors)

        emp = db.session.get(Employee, emp_id)
        if not emp:
            return False, "Employee not found."

        # Check email uniqueness (excluding self)
        new_email = data.get("email", emp.email).strip().lower()
        conflict = Employee.query.filter(
            Employee.email == new_email,
            Employee.id != emp_id
        ).first()
        if conflict:
            return False, f"Email '{new_email}' is already in use."

        emp.first_name    = data.get("first_name", emp.first_name).strip()
        emp.last_name     = data.get("last_name",  emp.last_name).strip()
        emp.email         = new_email
        emp.phone         = data.get("phone",    emp.phone or "").strip()
        emp.position      = data.get("position", emp.position or "").strip()
        emp.salary        = float(data.get("salary", emp.salary))
        emp.status        = data.get("status",   emp.status)
        dept_id           = data.get("department_id")
        emp.department_id = int(dept_id) if dept_id else emp.department_id
        if data.get("hire_date"):
            emp.hire_date = parse_date(data["hire_date"]) or emp.hire_date

        db.session.commit()
        return True, "Employee updated successfully."

    @staticmethod
    def delete(emp_id: int) -> tuple[bool, str]:
        """Soft-delete: mark employee status as terminated."""
        emp = db.session.get(Employee, emp_id)
        if not emp:
            return False, "Employee not found."
        emp.status = EmployeeStatus.TERMINATED.value
        db.session.commit()
        return True, "Employee marked as terminated."

    @staticmethod
    def hard_delete(emp_id: int) -> tuple[bool, str]:
        """Permanently delete an employee and all related records."""
        emp = db.session.get(Employee, emp_id)
        if not emp:
            return False, "Employee not found."
        db.session.delete(emp)
        db.session.commit()
        return True, "Employee deleted permanently."

    @staticmethod
    def count() -> int:
        return Employee.query.filter_by(status=EmployeeStatus.ACTIVE.value).count()

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _validate(data: dict, is_update: bool = False) -> list[str]:
        errors = []
        for field, label in [("first_name", "First Name"), ("last_name", "Last Name")]:
            if data.get(field) is not None or not is_update:
                ok, msg = validate_name(data.get(field, ""), label)
                if not ok:
                    errors.append(msg)
        if data.get("email") is not None or not is_update:
            ok, msg = validate_email(data.get("email", ""))
            if not ok:
                errors.append(msg)
        if data.get("phone"):
            ok, msg = validate_phone(data["phone"])
            if not ok:
                errors.append(msg)
        if data.get("salary") is not None:
            ok, msg = validate_salary(str(data.get("salary", "")))
            if not ok:
                errors.append(msg)
        if data.get("hire_date"):
            ok, msg = validate_date(data["hire_date"], "Hire date")
            if not ok:
                errors.append(msg)
        return errors

    @staticmethod
    def _to_dict(e: Employee) -> dict:
        if e is None:
            return {}
        return {
            "id":              e.id,
            "emp_code":        e.emp_code,
            "first_name":      e.first_name,
            "last_name":       e.last_name,
            "full_name":       e.full_name,
            "email":           e.email,
            "phone":           e.phone,
            "hire_date":       str(e.hire_date) if e.hire_date else "",
            "salary":          e.salary,
            "position":        e.position,
            "status":          e.status,
            "department_id":   e.department_id,
            "department_name": e.department.name if e.department else "—",
        }
