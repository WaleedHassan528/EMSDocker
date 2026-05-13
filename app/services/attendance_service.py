"""
Attendance service — mark, query, and summarize attendance records.
Flask-SQLAlchemy version.
"""
from datetime import date, timedelta

from app.extensions import db
from app.models.models import Attendance, AttendanceStatus
from app.utils.helpers import parse_date


class AttendanceService:

    @staticmethod
    def get_all(limit: int = 200) -> list[dict]:
        """Return the most recent attendance records."""
        records = (
            Attendance.query
            .order_by(Attendance.date.desc())
            .limit(limit)
            .all()
        )
        return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def get_for_employee(emp_id: int, days: int = 30) -> list[dict]:
        """Return attendance records for an employee over the last N days."""
        since = date.today() - timedelta(days=days)
        records = (
            Attendance.query
            .filter(
                Attendance.employee_id == emp_id,
                Attendance.date >= since,
            )
            .order_by(Attendance.date.desc())
            .all()
        )
        return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def get_today() -> list[dict]:
        """All attendance records for today."""
        today = date.today()
        records = Attendance.query.filter(Attendance.date == today).all()
        return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def mark(emp_id: int, att_date: str, check_in: str,
             check_out: str, status: str, notes: str = "") -> tuple[bool, str]:
        """Mark or update attendance for an employee on a given date."""
        d = parse_date(att_date)
        if not d:
            return False, "Invalid date format."
        if status not in [s.value for s in AttendanceStatus]:
            return False, f"Invalid status '{status}'."

        existing = Attendance.query.filter_by(
            employee_id=emp_id, date=d
        ).first()

        if existing:
            existing.check_in  = check_in
            existing.check_out = check_out
            existing.status    = status
            existing.notes     = notes
        else:
            record = Attendance(
                employee_id=emp_id,
                date=d,
                check_in=check_in,
                check_out=check_out,
                status=status,
                notes=notes,
            )
            db.session.add(record)

        db.session.commit()
        return True, "Attendance recorded."

    @staticmethod
    def delete(record_id: int) -> tuple[bool, str]:
        record = db.session.get(Attendance, record_id)
        if not record:
            return False, "Attendance record not found."
        db.session.delete(record)
        db.session.commit()
        return True, "Attendance record deleted."

    @staticmethod
    def today_count() -> dict:
        """Return count of present / absent / late / half_day for today."""
        today   = date.today()
        records = Attendance.query.filter(Attendance.date == today).all()
        counts  = {"present": 0, "absent": 0, "late": 0, "half_day": 0}
        for r in records:
            if r.status in counts:
                counts[r.status] += 1
        return counts

    @staticmethod
    def monthly_summary(emp_id: int, month: int, year: int) -> dict:
        """Summarise attendance for a given month."""
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        records = Attendance.query.filter(
            Attendance.employee_id == emp_id,
            Attendance.date >= date(year, month, 1),
            Attendance.date <= date(year, month, days_in_month),
        ).all()
        summary = {"present": 0, "absent": 0, "late": 0, "half_day": 0, "total": len(records)}
        for r in records:
            if r.status in summary:
                summary[r.status] += 1
        return summary

    @staticmethod
    def _to_dict(r: Attendance) -> dict:
        emp_name = r.employee.full_name if r.employee else ""
        return {
            "id":          r.id,
            "employee_id": r.employee_id,
            "emp_name":    emp_name,
            "date":        str(r.date),
            "check_in":    r.check_in,
            "check_out":   r.check_out,
            "status":      r.status,
            "notes":       r.notes,
        }
