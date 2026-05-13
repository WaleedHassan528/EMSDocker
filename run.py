"""
run.py — Entry point for the EMS Flask web application.

Usage:
    python run.py                    # Development server
    python run.py --seed             # Seed demo data then run
    flask run                        # Alternate (reads FLASK_APP=run.py)
"""
import os
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="EMS Flask Web Application")
    parser.add_argument("--seed", action="store_true",
                        help="Seed the database with demo data before starting.")
    parser.add_argument("--port", type=int, default=5000,
                        help="Port to run the server on (default: 5000).")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Host to bind the server to (default: 0.0.0.0).")
    args = parser.parse_args()

    from app import create_app
    from config import get_config

    app = create_app(get_config())

    with app.app_context():
        from app.extensions import db
        db.create_all()

        if args.seed:
            print("[EMS] Seeding demo data…")
            from database.seed_data import seed_database
            seed_database()
            print("[EMS] Seeding complete.")

    host = os.environ.get("FLASK_HOST", args.host)
    port = int(os.environ.get("FLASK_PORT", args.port))
    debug = os.environ.get("FLASK_ENV", "development") == "development"

    print(f"[EMS] Starting server on http://{host}:{port}  (debug={debug})")
    app.run(host=host, port=port, debug=debug)


# Expose `app` for `flask run` / gunicorn
from app import create_app
from config import get_config
app = create_app(get_config())


if __name__ == "__main__":
    main()
