"""
Leave routes — apply, list, approve, reject, delete.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user

from app.services.leave_service    import LeaveService
from app.services.employee_service import EmployeeService
from app.utils.decorators import admin_required
from app.utils.helpers import today_str

leave_bp = Blueprint("leave", __name__, url_prefix="/leave")


@leave_bp.route("/")
@login_required
def list_leave():
    status_filter = request.args.get("status", "")

    if current_user.is_admin:
        leaves = LeaveService.get_all(status_filter=status_filter or None)
    else:
        leaves = LeaveService.get_for_employee(current_user.employee_id)

    return render_template(
        "leave/list.html",
        leaves=leaves,
        status_filter=status_filter,
    )


@leave_bp.route("/apply", methods=["GET", "POST"])
@login_required
def apply_leave():
    # Admins can apply on behalf of any employee; employees apply for themselves
    employees = EmployeeService.get_all(status_filter="active") if current_user.is_admin else []

    if request.method == "POST":
        if current_user.is_admin:
            emp_id = request.form.get("employee_id", type=int)
        else:
            emp_id = current_user.employee_id

        leave_type = request.form.get("leave_type", "annual")
        start_date = request.form.get("start_date", "")
        end_date   = request.form.get("end_date", "")
        reason     = request.form.get("reason", "")

        success, result = LeaveService.apply(
            emp_id, leave_type, start_date, end_date, reason
        )
        if success:
            flash("Leave request submitted successfully.", "success")
            return redirect(url_for("leave.list_leave"))
        else:
            flash(result, "danger")

    return render_template(
        "leave/form.html",
        employees=employees,
        today=today_str(),
    )


@leave_bp.route("/<int:leave_id>/approve", methods=["POST"])
@admin_required
def approve_leave(leave_id):
    approver_id = current_user.employee_id
    success, message = LeaveService.approve(leave_id, approver_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("leave.list_leave"))


@leave_bp.route("/<int:leave_id>/reject", methods=["POST"])
@admin_required
def reject_leave(leave_id):
    approver_id = current_user.employee_id
    success, message = LeaveService.reject(leave_id, approver_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("leave.list_leave"))


@leave_bp.route("/<int:leave_id>/delete", methods=["POST"])
@login_required
def delete_leave(leave_id):
    leave = LeaveService.get_by_id(leave_id)
    if not leave:
        flash("Leave request not found.", "danger")
        return redirect(url_for("leave.list_leave"))

    # Only admin or the leave owner can delete
    if not current_user.is_admin and leave["employee_id"] != current_user.employee_id:
        flash("You cannot delete this leave request.", "danger")
        return redirect(url_for("leave.list_leave"))

    success, message = LeaveService.delete(leave_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("leave.list_leave"))
