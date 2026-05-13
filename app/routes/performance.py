"""
Performance review routes — list, add, edit, delete.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_required, current_user

from app.services.performance_service import PerformanceService
from app.services.employee_service    import EmployeeService
from app.utils.decorators import admin_required
from app.utils.helpers import today_str

performance_bp = Blueprint("performance", __name__, url_prefix="/performance")


@performance_bp.route("/")
@login_required
def list_performance():
    if current_user.is_admin:
        reviews = PerformanceService.get_all()
    else:
        reviews = PerformanceService.get_for_employee(current_user.employee_id)
    return render_template("performance/list.html", reviews=reviews)


@performance_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_review():
    employees = EmployeeService.get_all(status_filter="active")
    if request.method == "POST":
        emp_id      = request.form.get("employee_id", type=int)
        rating      = request.form.get("rating", 3, type=int)
        comments    = request.form.get("comments", "")
        review_date = request.form.get("review_date", "")
        success, message = PerformanceService.add_review(
            emp_id, current_user.employee_id, rating, comments, review_date or None
        )
        if success:
            flash("Performance review submitted.", "success")
            return redirect(url_for("performance.list_performance"))
        flash(message, "danger")
    return render_template("performance/form.html",
                           employees=employees, review=None, mode="add", today=today_str())


@performance_bp.route("/<int:review_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_review(review_id):
    review    = PerformanceService.get_by_id(review_id)
    employees = EmployeeService.get_all(status_filter="active")
    if not review:
        flash("Review not found.", "danger")
        return redirect(url_for("performance.list_performance"))
    if request.method == "POST":
        rating   = request.form.get("rating", 3, type=int)
        comments = request.form.get("comments", "")
        success, message = PerformanceService.update_review(review_id, rating, comments)
        if success:
            flash("Review updated successfully.", "success")
            return redirect(url_for("performance.list_performance"))
        flash(message, "danger")
    return render_template("performance/form.html",
                           employees=employees, review=review, mode="edit", today=today_str())


@performance_bp.route("/<int:review_id>/delete", methods=["POST"])
@admin_required
def delete_review(review_id):
    success, message = PerformanceService.delete_review(review_id)
    if request.is_json:
        return jsonify(success=success, message=message)
    flash(message, "success" if success else "danger")
    return redirect(url_for("performance.list_performance"))
