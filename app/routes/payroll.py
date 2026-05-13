"""
Payroll routes — list, generate payslip, view detail, delete.
"""
from datetime import date
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user

from app.services.payroll_service  import PayrollService
from app.services.employee_service import EmployeeService
from app.utils.decorators import admin_required

payroll_bp = Blueprint("payroll", __name__, url_prefix="/payroll")


@payroll_bp.route("/")
@login_required
def list_payroll():
    today = date.today()
    month = request.args.get("month", today.month, type=int)
    year  = request.args.get("year",  today.year,  type=int)

    if current_user.is_admin:
        records = PayrollService.get_all(month=month, year=year)
    else:
        records = PayrollService.get_for_employee(current_user.employee_id)

    return render_template(
        "payroll/list.html",
        records=records,
        month=month,
        year=year,
        today=today,
    )


@payroll_bp.route("/generate", methods=["GET", "POST"])
@admin_required
def generate_payroll():
    employees = EmployeeService.get_all(status_filter="active")
    today     = date.today()
    payslip   = None

    if request.method == "POST":
        emp_id           = request.form.get("employee_id", type=int)
        month            = request.form.get("month", today.month, type=int)
        year             = request.form.get("year",  today.year,  type=int)
        extra_allowances = request.form.get("extra_allowances", 0.0, type=float)
        extra_deductions = request.form.get("extra_deductions", 0.0, type=float)

        success, result = PayrollService.generate(
            emp_id, month, year, extra_allowances, extra_deductions
        )
        if success:
            payslip = result
            flash("Payslip generated successfully.", "success")
        else:
            flash(result, "danger")

    return render_template(
        "payroll/generate.html",
        employees=employees,
        today=today,
        payslip=payslip,
    )


@payroll_bp.route("/<int:payroll_id>/payslip")
@login_required
def payslip(payroll_id):
    """Regenerate a payslip view from a stored payroll record."""
    from app.models.models import Payroll
    from app.extensions import db
    p = db.session.get(Payroll, payroll_id)
    if not p:
        flash("Payroll record not found.", "danger")
        return redirect(url_for("payroll.list_payroll"))

    # Non-admin can only see their own payslips
    if not current_user.is_admin and p.employee_id != current_user.employee_id:
        flash("You can only view your own payslips.", "warning")
        return redirect(url_for("payroll.list_payroll"))

    success, payslip_data = PayrollService.generate(
        p.employee_id, p.month, p.year
    )
    if not success:
        flash(payslip_data, "danger")
        return redirect(url_for("payroll.list_payroll"))

    return render_template("payroll/payslip.html", payslip=payslip_data)


@payroll_bp.route("/<int:payroll_id>/delete", methods=["POST"])
@admin_required
def delete_payroll(payroll_id):
    success, message = PayrollService.delete(payroll_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("payroll.list_payroll"))
