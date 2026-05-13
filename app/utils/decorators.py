"""
Route decorators for authentication and authorization.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def login_required_custom(f):
    """Ensure the user is logged in before accessing a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Restrict a route to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            flash("You do not have permission to access this page.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated
