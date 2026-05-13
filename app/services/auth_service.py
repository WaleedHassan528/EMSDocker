"""
Authentication service — login, logout, user management.
Adapted for Flask-Login session management (no more class-level _current_user).
"""
from datetime import datetime
from flask_login import login_user, logout_user

from app.extensions import db
from app.models.models import User, UserRole
from app.utils.helpers import verify_password, hash_password
from app.utils.validators import validate_username, validate_password


class AuthService:

    # ── Login / Logout ────────────────────────────────────────────────────────

    @staticmethod
    def login(username: str, password: str, remember: bool = False) -> tuple[bool, str]:
        """
        Attempt to log in.  On success, calls Flask-Login login_user().
        Returns (success, message).
        """
        valid_u, err_u = validate_username(username)
        if not valid_u:
            return False, err_u

        valid_p, err_p = validate_password(password)
        if not valid_p:
            return False, err_p

        user = User.query.filter_by(username=username.strip(), is_active=True).first()

        if not user or not verify_password(password, user.password_hash):
            return False, "Invalid username or password."

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        return True, "Login successful."

    @staticmethod
    def logout():
        """Log out the current Flask-Login user."""
        logout_user()

    # ── User Management ───────────────────────────────────────────────────────

    @staticmethod
    def create_user(username: str, password: str, role: str,
                    employee_id: int | None = None) -> tuple[bool, str]:
        """Create a new user account (admin only)."""
        valid_u, err_u = validate_username(username)
        if not valid_u:
            return False, err_u

        valid_p, err_p = validate_password(password)
        if not valid_p:
            return False, err_p

        existing = User.query.filter_by(username=username.strip()).first()
        if existing:
            return False, f"Username '{username}' already exists."

        user = User(
            username=username.strip(),
            password_hash=hash_password(password),
            role=role,
            employee_id=employee_id,
        )
        db.session.add(user)
        db.session.commit()
        return True, "User created successfully."

    @staticmethod
    def change_password(user_id: int, old_password: str,
                        new_password: str) -> tuple[bool, str]:
        """Change a user's password after verifying the old password."""
        valid_p, err_p = validate_password(new_password)
        if not valid_p:
            return False, err_p

        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found."
        if not verify_password(old_password, user.password_hash):
            return False, "Incorrect current password."

        user.password_hash = hash_password(new_password)
        db.session.commit()
        return True, "Password changed successfully."

    @staticmethod
    def get_all_users() -> list[dict]:
        """Return all user records as a list of dicts."""
        users = User.query.all()
        return [
            {
                "id":          u.id,
                "username":    u.username,
                "role":        u.role,
                "employee_id": u.employee_id,
                "is_active":   u.is_active,
            }
            for u in users
        ]

    @staticmethod
    def toggle_active(user_id: int) -> tuple[bool, str]:
        """Toggle a user account's active/inactive status."""
        user = db.session.get(User, user_id)
        if not user:
            return False, "User not found."
        user.is_active = not user.is_active
        db.session.commit()
        state = "activated" if user.is_active else "deactivated"
        return True, f"User {state} successfully."
