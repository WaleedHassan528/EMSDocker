"""
Department routes — list, add, edit, delete.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required

from app.services.department_service import DepartmentService
from app.utils.decorators import admin_required

departments_bp = Blueprint("departments", __name__, url_prefix="/departments")


@departments_bp.route("/")
@login_required
def list_departments():
    departments = DepartmentService.get_employee_counts()
    return render_template("departments/list.html", departments=departments)


@departments_bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_department():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        success, result = DepartmentService.create(name, description)
        if success:
            flash("Department created successfully.", "success")
            return redirect(url_for("departments.list_departments"))
        else:
            flash(result, "danger")
    return render_template("departments/form.html", department=None, mode="new")


@departments_bp.route("/<int:dept_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_department(dept_id):
    department = DepartmentService.get_by_id(dept_id)
    if not department:
        flash("Department not found.", "danger")
        return redirect(url_for("departments.list_departments"))

    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        success, message = DepartmentService.update(dept_id, name, description)
        if success:
            flash("Department updated successfully.", "success")
            return redirect(url_for("departments.list_departments"))
        else:
            flash(message, "danger")

    return render_template("departments/form.html",
                           department=department, mode="edit")


@departments_bp.route("/<int:dept_id>/delete", methods=["POST"])
@admin_required
def delete_department(dept_id):
    success, message = DepartmentService.delete(dept_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("departments.list_departments"))
