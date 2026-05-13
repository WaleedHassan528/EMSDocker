"""
Attendance routes — list all, mark attendance, delete records.
"""
from datetime import date
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user

from app.services.attendance_service import AttendanceService
from app.services.employee_service   import EmployeeService
from app.utils.decorators import admin_required
from app.utils.helpers import today_str

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@attendance_bp.route("/")
@login_required
def list_attendance():
    # Admins see all; employees see only their own
    if current_user.is_admin:
        records = AttendanceService.get_all(limit=300)
    else:
        records = AttendanceService.get_for_employee(
            current_user.employee_id, days=60
        )
    return render_template("attendance/list.html", records=records, today=today_str())


@attendance_bp.route("/mark", methods=["GET", "POST"])
@admin_required
def mark_attendance():
    employees = EmployeeService.get_all(status_filter="active")

    if request.method == "POST":
        emp_id    = request.form.get("employee_id", type=int)
        att_date  = request.form.get("date", today_str())
        check_in  = request.form.get("check_in", "")
        check_out = request.form.get("check_out", "")
        status    = request.form.get("status", "present")
        notes     = request.form.get("notes", "")

        success, message = AttendanceService.mark(
            emp_id, att_date, check_in, check_out, status, notes
        )
        if success:
            flash("Attendance recorded successfully.", "success")
            return redirect(url_for("attendance.list_attendance"))
        else:
            flash(message, "danger")

    return render_template(
        "attendance/form.html",
        employees=employees,
        today=today_str(),
    )


@attendance_bp.route("/<int:record_id>/delete", methods=["POST"])
@admin_required
def delete_record(record_id):
    success, message = AttendanceService.delete(record_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("attendance.list_attendance"))
