"""
Employee routes — list, add, edit, view detail, delete.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user

from app.services.employee_service   import EmployeeService
from app.services.department_service import DepartmentService
from app.utils.decorators import admin_required

employees_bp = Blueprint("employees", __name__, url_prefix="/employees")


@employees_bp.route("/")
@login_required
def list_employees():
    status_filter = request.args.get("status", "")
    search_query  = request.args.get("q", "").strip()

    if search_query:
        employees = EmployeeService.search(search_query)
    elif status_filter:
        employees = EmployeeService.get_all(status_filter=status_filter)
    else:
        employees = EmployeeService.get_all()

    return render_template(
        "employees/list.html",
        employees     = employees,
        status_filter = status_filter,
        search_query  = search_query,
    )


@employees_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_employee():
    departments = DepartmentService.get_all()

    if request.method == "POST":
        data = {
            "emp_code":      request.form.get("emp_code", "").strip(),
            "first_name":    request.form.get("first_name", "").strip(),
            "last_name":     request.form.get("last_name", "").strip(),
            "email":         request.form.get("email", "").strip(),
            "phone":         request.form.get("phone", "").strip(),
            "position":      request.form.get("position", "").strip(),
            "salary":        request.form.get("salary", "0"),
            "hire_date":     request.form.get("hire_date", ""),
            "department_id": request.form.get("department_id", ""),
            "status":        request.form.get("status", "active"),
        }
        success, result = EmployeeService.create(data)
        if success:
            flash("Employee added successfully.", "success")
            return redirect(url_for("employees.detail", emp_id=result))
        else:
            flash(result, "danger")

    return render_template("employees/form.html",
                           departments=departments, employee=None, mode="new")


@employees_bp.route("/<int:emp_id>")
@login_required
def detail(emp_id):
    # Employees can only view their own profile
    if not current_user.is_admin and current_user.employee_id != emp_id:
        flash("You can only view your own profile.", "warning")
        return redirect(url_for("employees.detail",
                                emp_id=current_user.employee_id))

    employee = EmployeeService.get_by_id(emp_id)
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/detail.html", employee=employee)


@employees_bp.route("/<int:emp_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_employee(emp_id):
    employee    = EmployeeService.get_by_id(emp_id)
    departments = DepartmentService.get_all()

    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees.list_employees"))

    if request.method == "POST":
        data = {
            "first_name":    request.form.get("first_name", "").strip(),
            "last_name":     request.form.get("last_name", "").strip(),
            "email":         request.form.get("email", "").strip(),
            "phone":         request.form.get("phone", "").strip(),
            "position":      request.form.get("position", "").strip(),
            "salary":        request.form.get("salary", "0"),
            "hire_date":     request.form.get("hire_date", ""),
            "department_id": request.form.get("department_id", ""),
            "status":        request.form.get("status", "active"),
        }
        success, message = EmployeeService.update(emp_id, data)
        if success:
            flash("Employee updated successfully.", "success")
            return redirect(url_for("employees.detail", emp_id=emp_id))
        else:
            flash(message, "danger")

    return render_template("employees/form.html",
                           employee=employee, departments=departments, mode="edit")


@employees_bp.route("/<int:emp_id>/delete", methods=["POST"])
@admin_required
def delete_employee(emp_id):
    delete_type = request.form.get("delete_type", "soft")
    if delete_type == "hard":
        success, message = EmployeeService.hard_delete(emp_id)
    else:
        success, message = EmployeeService.delete(emp_id)

    if request.is_json:
        return jsonify(success=success, message=message)

    flash(message, "success" if success else "danger")
    return redirect(url_for("employees.list_employees"))
