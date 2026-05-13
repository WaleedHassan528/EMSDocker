"""
Flask Application Factory.
Creates and configures the Flask application instance.
"""
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from .extensions import db, login_manager


def create_app(config=None) -> Flask:
    """
    Application factory pattern.
    Accepts a config object or class; falls back to environment-based defaults.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ── Load Configuration ─────────────────────────────────────────────────────
    if config is None:
        from config import get_config
        config = get_config()
    app.config.from_object(config)

    # ── Initialise Extensions ─────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    # ── User Loader ───────────────────────────────────────────────────────────
    from .models.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ── Register Blueprints ────────────────────────────────────────────────────
    from .routes.auth        import auth_bp
    from .routes.dashboard   import dashboard_bp
    from .routes.employees   import employees_bp
    from .routes.departments import departments_bp
    from .routes.attendance  import attendance_bp
    from .routes.leave       import leave_bp
    from .routes.payroll     import payroll_bp
    from .routes.performance import performance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(performance_bp)

    # ── Jinja2 Globals ─────────────────────────────────────────────────────────
    from .utils.helpers import format_currency, format_date, badge_class, month_name
    app.jinja_env.globals.update(
        format_currency=format_currency,
        format_date=format_date,
        badge_class=badge_class,
        month_name=month_name,
    )

    # ── Logging ────────────────────────────────────────────────────────────────
    _configure_logging(app)

    # ── Shell Context ─────────────────────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from .models.models import (Department, Employee, User,
                                     Attendance, Leave, Payroll, Performance)
        return dict(db=db, Department=Department, Employee=Employee,
                    User=User, Attendance=Attendance, Leave=Leave,
                    Payroll=Payroll, Performance=Performance)

    return app


def _configure_logging(app: Flask):
    """Set up rotating file + console logging."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    log_file  = app.config.get("LOG_FILE", "logs/ems.log")

    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(log_level)

    # File handler (5 MB × 3 backups)
    try:
        file_handler = RotatingFileHandler(log_file, maxBytes=5_242_880, backupCount=3)
        file_handler.setFormatter(fmt)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    except Exception:
        pass  # Non-fatal if log directory isn't writable

    app.logger.addHandler(console)
    app.logger.setLevel(log_level)
    app.logger.info("EMS Flask application started.")
