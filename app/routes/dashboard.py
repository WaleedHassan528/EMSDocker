"""
Dashboard routes — main overview page.
"""
from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.services.employee_service   import EmployeeService
from app.services.attendance_service import AttendanceService
from app.services.leave_service      import LeaveService
from app.services.department_service import DepartmentService
from app.services.payroll_service    import PayrollService
from app.services.performance_service import PerformanceService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    today = date.today()

    # ── Stats cards ───────────────────────────────────────────────────────────
    total_employees  = EmployeeService.count()
    pending_leaves   = LeaveService.pending_count()
    attendance_today = AttendanceService.today_count()
    departments      = DepartmentService.get_employee_counts()

    # ── Recent payroll (current month) ────────────────────────────────────────
    recent_payroll = PayrollService.get_all(month=today.month, year=today.year)

    # ── Recent performance reviews ────────────────────────────────────────────
    recent_reviews = PerformanceService.get_all()[:5]

    # ── Dept distribution for chart ───────────────────────────────────────────
    dept_labels = [d["name"] for d in departments]
    dept_counts = [d["employee_count"] for d in departments]

    # ── Today's attendance breakdown ──────────────────────────────────────────
    att_labels = ["Present", "Absent", "Late", "Half Day"]
    att_data   = [
        attendance_today.get("present", 0),
        attendance_today.get("absent",  0),
        attendance_today.get("late",    0),
        attendance_today.get("half_day",0),
    ]

    return render_template(
        "dashboard/index.html",
        total_employees  = total_employees,
        pending_leaves   = pending_leaves,
        attendance_today = attendance_today,
        departments      = departments,
        recent_payroll   = recent_payroll[:5],
        recent_reviews   = recent_reviews,
        dept_labels      = dept_labels,
        dept_counts      = dept_counts,
        att_labels       = att_labels,
        att_data         = att_data,
        today            = today,
    )
