# waleed Hassan
# ⚡ EMS Pro — Employee Management System

EMS Pro is a professional, Flask-based web application converted from a desktop management system. It features a modern glassmorphism design, role-based access control, and comprehensive employee management modules.

## ✨ Key Features

- **Dashboard:** Visual overview with Chart.js analytics.
- **Employee Management:** Full CRUD with search and status filtering.
- **Department Management:** Organized structure with employee tracking.
- **Attendance Tracking:** Check-in/out logging with status management.
- **Leave Management:** Application and multi-level approval workflow.
- **Payroll System:** Automatic payslip generation with tax and allowance calculations.
- **Performance Reviews:** 5-star rating system with historical tracking.

## 🚀 Quick Start (Local Run)

### 1. Prerequisites
- Python 3.10+
- Virtual Environment (recommended)

### 2. Setup
```bash
# Navigate to project
cd WEB_END

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialise and Seed Database
python run.py --seed
```

### 3. Run
```bash
python run.py
```
Access the app at: `http://localhost:5000`

**Demo Credentials:**
- **Admin:** `admin` / `admin123`
- **Employee:** `bob` / `pass123`

---

## 🐳 Docker Deployment

To run the entire stack using Docker:

```bash
# Build and start container
docker-compose up --build -d

# Initialise database in container (first time only)
docker-compose exec web python run.py --seed
```

---

## 📂 Project Structure

- `app/`: Core application logic (Routes, Services, Models).
- `static/`: Modern design system (CSS/JS).
- `templates/`: Jinja2 UI templates.
- `database/`: Seeding and initial setup.
- `config.py`: Environment-aware configuration.

## 🛠 Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Vanilla CSS (Glassmorphism), Vanilla JS, Chart.js
- **Deployment:** Docker, Gunicorn
