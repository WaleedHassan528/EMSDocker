"""
Shared utility helpers — password hashing, formatting, badge utilities.
Preserved from the original desktop EMS; adapted for Flask context.
"""
import hashlib
import secrets
from datetime import datetime, date


# ─── Password Hashing (SHA-256 + salt) ───────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plaintext password with a random salt using SHA-256."""
    salt   = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + plain).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, stored_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        salt, hashed = stored_hash.split(":", 1)
        return hashlib.sha256((salt + plain).encode()).hexdigest() == hashed
    except Exception:
        return False


# ─── Formatting ───────────────────────────────────────────────────────────────

def format_currency(amount: float, symbol: str = "$") -> str:
    """Format a number as a currency string."""
    try:
        return f"{symbol}{float(amount):,.2f}"
    except (TypeError, ValueError):
        return f"{symbol}0.00"


def format_date(d) -> str:
    """Format a date/datetime to DD Mon YYYY string."""
    if d is None:
        return "—"
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    return d.strftime("%d %b %Y")


def parse_date(date_str: str) -> date | None:
    """Parse YYYY-MM-DD (or MM/DD/YYYY, DD-MM-YYYY) string to date object."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def month_name(month_num: int) -> str:
    """Return full month name from integer (1-12)."""
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return str(month_num)


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().strftime("%Y-%m-%d")


def generate_emp_code(existing_codes: list[str]) -> str:
    """Auto-generate a unique employee code like EMP009."""
    nums = []
    for code in existing_codes:
        try:
            nums.append(int(code.replace("EMP", "")))
        except ValueError:
            pass
    next_num = max(nums, default=0) + 1
    return f"EMP{next_num:03d}"


def truncate(text: str, max_len: int = 30) -> str:
    """Truncate a string and add ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


# ─── Badge CSS class helper (replaces badge_color hex in the web version) ─────

def badge_class(status: str) -> str:
    """
    Return a CSS badge class for a given status string.
    Used as a Jinja2 global in templates.
    """
    mapping = {
        "approved":   "badge-success",
        "present":    "badge-success",
        "active":     "badge-success",
        "pending":    "badge-warning",
        "late":       "badge-warning",
        "half_day":   "badge-warning",
        "rejected":   "badge-danger",
        "absent":     "badge-danger",
        "inactive":   "badge-danger",
        "terminated": "badge-secondary",
    }
    return mapping.get((status or "").lower(), "badge-secondary")


def stars(rating: int) -> str:
    """Return a star string representation of a 1-5 rating."""
    try:
        r = max(1, min(5, int(rating)))
    except (TypeError, ValueError):
        r = 0
    return "★" * r + "☆" * (5 - r)
