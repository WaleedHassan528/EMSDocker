"""
Auth routes — login and logout.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import current_user, logout_user

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        success, message = AuthService.login(username, password, remember)
        if success:
            flash("Welcome back! You are now logged in.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash(message, "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    AuthService.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
