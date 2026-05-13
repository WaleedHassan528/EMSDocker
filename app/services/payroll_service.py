"""
Payroll service — generate payslips using attendance data.
Flask-SQLAlchemy version; all calculation logic is preserved.
"""
from datetime import date
from calendar import monthrange

from app.extensions import db
from app.models.models import Payroll, Employee, Attendance, AttendanceStatus
from app.utils.helpers import format_currency, month_name
from app.utils.validators import validate_allowance_deduction


class PayrollService:

    @staticmethod
    def get_all(month: int | None = None, year: int | None = None) -> list[dict]:
        q = Payroll.query
        if month:
            q = q.filter_by(month=month)
        if year:
            q = q.filter_by(year=year)
        records = q.order_by(Payroll.year.desc(), Payroll.month.desc()).all()
        return [PayrollService._to_dict(p) for p in records]

    @staticmethod
    def get_for_employee(emp_id: int) -> list[dict]:
        records = (
            Payroll.query
            .filter_by(employee_id=emp_id)
            .order_by(Payroll.year.desc(), Payroll.month.desc())
            .all()
        )
        return [PayrollService._to_dict(p) for p in records]

    @staticmethod
    def generate(emp_id: int, month: int, year: int,
                 extra_allowances: float = 0.0,
                 extra_deductions: float = 0.0) -> tuple[bool, str | dict]:
        """
        Generate or regenerate a payslip for an employee.
        Returns (True, payslip_dict) or (False, error_message).
        """
        ok_a, err_a = validate_allowance_deduction(str(extra_allowances), "Allowances")
        if not ok_a:
            return False, err_a
        ok_d, err_d = validate_allowance_deduction(str(extra_deductions), "Deductions")
        if not ok_d:
            return False, err_d

        if not (1 <= month <= 12):
            return False, "Month must be between 1 and 12."
        if year < 2000 or year > date.today().year + 1:
            return False, "Invalid year."

        emp = db.session.get(Employee, emp_id)
        if not emp:
            return False, "Employee not found."

        existing = Payroll.query.filter_by(
            employee_id=emp_id, month=month, year=year
        ).first()

        # ── Attendance data ───────────────────────────────────────────────────
        _, days_in_month = monthrange(year, month)
        first_day = date(year, month, 1)
        last_day  = date(year, month, days_in_month)

        att_records = Attendance.query.filter(
            Attendance.employee_id == emp_id,
            Attendance.date >= first_day,
            Attendance.date <= last_day,
        ).all()

        working_days = sum(
            1 for day in range(days_in_month)
            if date(year, month, day + 1).weekday() < 5
        )
        present_days = sum(
            1 for r in att_records
            if r.status in [AttendanceStatus.PRESENT.value, AttendanceStatus.LATE.value]
        )

        # ── Payroll calculations ──────────────────────────────────────────────
        base_salary   = emp.salary
        per_day       = base_salary / working_days if working_days > 0 else 0
        prorated_base = per_day * present_days
        allowances    = (base_salary * 0.10) + extra_allowances   # 10 % HRA + extras
        tax_rate      = 0.08 if base_salary > 50_000 else 0.05    # simple progressive tax
        tax           = prorated_base * tax_rate
        deductions    = tax + extra_deductions
        net_pay       = prorated_base + allowances - deductions

        if existing:
            existing.base_salary  = base_salary
            existing.allowances   = allowances
            existing.deductions   = deductions
            existing.net_pay      = net_pay
            existing.working_days = working_days
            existing.present_days = present_days
            existing.generated_on = date.today()
            payroll = existing
        else:
            payroll = Payroll(
                employee_id=emp_id,
                month=month,
                year=year,
                base_salary=base_salary,
                allowances=allowances,
                deductions=deductions,
                net_pay=net_pay,
                working_days=working_days,
                present_days=present_days,
            )
            db.session.add(payroll)

        db.session.commit()

        result = {
            "id":             payroll.id,
            "employee_id":    emp_id,
            "emp_name":       emp.full_name,
            "emp_code":       emp.emp_code,
            "position":       emp.position,
            "department":     emp.department.name if emp.department else "—",
            "month":          month,
            "month_name":     month_name(month),
            "year":           year,
            "base_salary":    base_salary,
            "prorated_base":  prorated_base,
            "allowances":     allowances,
            "deductions":     deductions,
            "net_pay":        net_pay,
            "working_days":   working_days,
            "present_days":   present_days,
            "absent_days":    working_days - present_days,
            "tax":            tax,
            "generated_on":   str(date.today()),
            "fmt_base":       format_currency(base_salary),
            "fmt_prorated":   format_currency(prorated_base),
            "fmt_allowances": format_currency(allowances),
            "fmt_deductions": format_currency(deductions),
            "fmt_net":        format_currency(net_pay),
            "fmt_tax":        format_currency(tax),
        }
        return True, result

    @staticmethod
    def delete(payroll_id: int) -> tuple[bool, str]:
        p = db.session.get(Payroll, payroll_id)
        if not p:
            return False, "Payroll record not found."
        db.session.delete(p)
        db.session.commit()
        return True, "Payroll record deleted."

    @staticmethod
    def _to_dict(p: Payroll) -> dict:
        return {
            "id":           p.id,
            "employee_id":  p.employee_id,
            "emp_name":     p.employee.full_name if p.employee else "—",
            "month":        p.month,
            "month_name":   month_name(p.month),
            "year":         p.year,
            "base_salary":  p.base_salary,
            "allowances":   p.allowances,
            "deductions":   p.deductions,
            "net_pay":      p.net_pay,
            "working_days": p.working_days,
            "present_days": p.present_days,
            "fmt_net":      format_currency(p.net_pay),
        }
