"""
Department management service — Flask-SQLAlchemy version.
"""
from app.extensions import db
from app.models.models import Department, Employee


class DepartmentService:

    @staticmethod
    def get_all() -> list[dict]:
        depts = Department.query.order_by(Department.name).all()
        return [DepartmentService._to_dict(d) for d in depts]

    @staticmethod
    def get_by_id(dept_id: int) -> dict | None:
        d = db.session.get(Department, dept_id)
        return DepartmentService._to_dict(d) if d else None

    @staticmethod
    def create(name: str, description: str = "") -> tuple[bool, str]:
        if not name or not name.strip():
            return False, "Department name is required."
        if len(name.strip()) > 100:
            return False, "Department name is too long (max 100 chars)."

        existing = Department.query.filter(
            Department.name.ilike(name.strip())
        ).first()
        if existing:
            return False, f"Department '{name}' already exists."

        dept = Department(name=name.strip(), description=description.strip())
        db.session.add(dept)
        db.session.commit()
        return True, str(dept.id)

    @staticmethod
    def update(dept_id: int, name: str, description: str = "") -> tuple[bool, str]:
        if not name or not name.strip():
            return False, "Department name is required."

        dept = db.session.get(Department, dept_id)
        if not dept:
            return False, "Department not found."

        conflict = Department.query.filter(
            Department.name.ilike(name.strip()),
            Department.id != dept_id
        ).first()
        if conflict:
            return False, f"Department '{name}' already exists."

        dept.name        = name.strip()
        dept.description = description.strip()
        db.session.commit()
        return True, "Department updated."

    @staticmethod
    def delete(dept_id: int) -> tuple[bool, str]:
        dept = db.session.get(Department, dept_id)
        if not dept:
            return False, "Department not found."
        count = Employee.query.filter_by(department_id=dept_id).count()
        if count > 0:
            return False, (
                f"Cannot delete department with {count} assigned employee(s). "
                "Reassign them first."
            )
        db.session.delete(dept)
        db.session.commit()
        return True, "Department deleted."

    @staticmethod
    def get_employee_counts() -> list[dict]:
        """Return each department with its employee count."""
        depts = Department.query.all()
        result = []
        for d in depts:
            count = Employee.query.filter_by(department_id=d.id).count()
            result.append({
                "id":             d.id,
                "name":           d.name,
                "description":    d.description,
                "employee_count": count,
            })
        return sorted(result, key=lambda x: x["name"])

    @staticmethod
    def _to_dict(d: Department) -> dict:
        if d is None:
            return {}
        return {
            "id":          d.id,
            "name":        d.name,
            "description": d.description,
            "created_at":  str(d.created_at),
        }
