"""
Input validation utilities.
All validators return (is_valid: bool, error_message: str).
Preserved from the original desktop EMS.
"""
import re
from datetime import date, datetime


# ─── Email ────────────────────────────────────────────────────────────────────

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email: str) -> tuple[bool, str]:
    if not email or not email.strip():
        return False, "Email is required."
    if not EMAIL_REGEX.match(email.strip()):
        return False, "Invalid email format. Example: user@example.com"
    return True, ""


# ─── Phone ────────────────────────────────────────────────────────────────────

PHONE_REGEX = re.compile(r"^\+?[\d\s\-().]{7,20}$")


def validate_phone(phone: str) -> tuple[bool, str]:
    if not phone or not phone.strip():
        return True, ""   # optional field
    if not PHONE_REGEX.match(phone.strip()):
        return False, "Invalid phone number format."
    return True, ""


# ─── Name ─────────────────────────────────────────────────────────────────────

def validate_name(name: str, field: str = "Name") -> tuple[bool, str]:
    if not name or not name.strip():
        return False, f"{field} is required."
    if len(name.strip()) < 2:
        return False, f"{field} must be at least 2 characters."
    if len(name.strip()) > 50:
        return False, f"{field} must not exceed 50 characters."
    if not re.match(r"^[a-zA-Z\s'\-]+$", name.strip()):
        return False, f"{field} can only contain letters, spaces, hyphens, and apostrophes."
    return True, ""


# ─── Salary ───────────────────────────────────────────────────────────────────

def validate_salary(salary_str: str) -> tuple[bool, str]:
    if not salary_str or not salary_str.strip():
        return False, "Salary is required."
    try:
        salary = float(salary_str.strip())
    except ValueError:
        return False, "Salary must be a valid number."
    if salary < 0:
        return False, "Salary cannot be negative."
    if salary > 10_000_000:
        return False, "Salary exceeds the maximum allowed value."
    return True, ""


# ─── Date ─────────────────────────────────────────────────────────────────────

def validate_date(date_str: str, field: str = "Date") -> tuple[bool, str]:
    if not date_str or not date_str.strip():
        return False, f"{field} is required."
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            datetime.strptime(date_str.strip(), fmt)
            return True, ""
        except ValueError:
            continue
    return False, f"{field} must be in YYYY-MM-DD format."


def validate_date_range(start_str: str, end_str: str) -> tuple[bool, str]:
    valid_s, err_s = validate_date(start_str, "Start date")
    if not valid_s:
        return False, err_s
    valid_e, err_e = validate_date(end_str, "End date")
    if not valid_e:
        return False, err_e
    start = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
    end   = datetime.strptime(end_str.strip(),   "%Y-%m-%d").date()
    if start > end:
        return False, "Start date cannot be after end date."
    return True, ""


# ─── Username / Password ──────────────────────────────────────────────────────

def validate_username(username: str) -> tuple[bool, str]:
    if not username or not username.strip():
        return False, "Username is required."
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if len(username.strip()) > 50:
        return False, "Username must not exceed 50 characters."
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username.strip()):
        return False, "Username can only contain letters, numbers, underscores, dots, and dashes."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    if not password:
        return False, "Password is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


# ─── Rating ───────────────────────────────────────────────────────────────────

def validate_rating(rating) -> tuple[bool, str]:
    try:
        r = int(rating)
    except (TypeError, ValueError):
        return False, "Rating must be a whole number."
    if not (1 <= r <= 5):
        return False, "Rating must be between 1 and 5."
    return True, ""


# ─── Employee Code ────────────────────────────────────────────────────────────

def validate_emp_code(code: str) -> tuple[bool, str]:
    if not code or not code.strip():
        return False, "Employee code is required."
    if not re.match(r"^[A-Z]{2,5}\d{3,6}$", code.strip().upper()):
        return False, "Employee code must be like EMP001 (2-5 letters + 3-6 digits)."
    return True, ""


# ─── Allowance / Deduction ────────────────────────────────────────────────────

def validate_allowance_deduction(value_str: str, field: str = "Value") -> tuple[bool, str]:
    if not value_str or not value_str.strip():
        return True, ""   # optional
    try:
        val = float(value_str.strip())
    except ValueError:
        return False, f"{field} must be a valid number."
    if val < 0:
        return False, f"{field} cannot be negative."
    return True, ""
