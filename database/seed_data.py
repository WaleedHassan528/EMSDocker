"""
Seed the database with initial demo data.
Called via `python run.py --seed` or imported at startup.
"""
from datetime import date, timedelta

from app.extensions import db
from app.models.models import (
    Department, Employee, User, Attendance, Leave,
    Payroll, Performance,
    AttendanceStatus, LeaveStatus, LeaveType, UserRole,
)
from app.utils.helpers import hash_password


def seed_database():
    """Insert demo data only if the database is empty."""
    if User.query.count() > 0:
        print("[Seed] Database already seeded — skipping.")
        return

    # ── Departments ───────────────────────────────────────────────────────────
    departments = [
        Department(name="Engineering",     description="Software & Hardware development"),
        Department(name="Human Resources", description="Recruitment and employee welfare"),
        Department(name="Finance",         description="Budgeting and accounting"),
        Department(name="Marketing",       description="Brand and growth"),
        Department(name="Operations",      description="Day-to-day business operations"),
    ]
    db.session.add_all(departments)
    db.session.flush()
    dept_map = {d.name: d for d in departments}

    # ── Employees ─────────────────────────────────────────────────────────────
    employees_data = [
        ("EMP001", "Alice",  "Johnson",  "alice@company.com",  "+1-555-0101", dept_map["Engineering"],     "Senior Engineer",   95000.0, date(2020, 3, 15)),
        ("EMP002", "Bob",    "Smith",    "bob@company.com",    "+1-555-0102", dept_map["Engineering"],     "Junior Engineer",   65000.0, date(2021, 6, 1)),
        ("EMP003", "Carol",  "Davis",    "carol@company.com",  "+1-555-0103", dept_map["Human Resources"], "HR Manager",        80000.0, date(2019, 1, 10)),
        ("EMP004", "David",  "Wilson",   "david@company.com",  "+1-555-0104", dept_map["Finance"],         "Accountant",        72000.0, date(2020, 8, 20)),
        ("EMP005", "Emma",   "Brown",    "emma@company.com",   "+1-555-0105", dept_map["Marketing"],       "Marketing Lead",    78000.0, date(2021, 2, 14)),
        ("EMP006", "Frank",  "Miller",   "frank@company.com",  "+1-555-0106", dept_map["Operations"],      "Ops Coordinator",   60000.0, date(2022, 5, 5)),
        ("EMP007", "Grace",  "Taylor",   "grace@company.com",  "+1-555-0107", dept_map["Engineering"],     "QA Engineer",       70000.0, date(2021, 9, 20)),
        ("EMP008", "Henry",  "Anderson", "henry@company.com",  "+1-555-0108", dept_map["Finance"],         "Finance Director", 110000.0, date(2018, 4, 2)),
    ]

    employees = []
    for code, fn, ln, email, phone, dept, pos, sal, hire in employees_data:
        emp = Employee(
            emp_code=code, first_name=fn, last_name=ln,
            email=email, phone=phone, department=dept,
            position=pos, salary=sal, hire_date=hire,
        )
        db.session.add(emp)
        employees.append(emp)
    db.session.flush()

    # ── Users ─────────────────────────────────────────────────────────────────
    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN.value,
        employee_id=employees[0].id,
    )
    db.session.add(admin)

    for emp in employees[1:]:
        user = User(
            username=emp.first_name.lower(),
            password_hash=hash_password("pass123"),
            role=UserRole.EMPLOYEE.value,
            employee_id=emp.id,
        )
        db.session.add(user)
    db.session.flush()

    # ── Attendance (last 30 days, weekdays only) ───────────────────────────────
    statuses = (
        [AttendanceStatus.PRESENT.value] * 7
        + [AttendanceStatus.LATE.value]
        + [AttendanceStatus.ABSENT.value]
    )
    today = date.today()

    for emp in employees:
        for days_back in range(30):
            att_date = today - timedelta(days=days_back)
            if att_date.weekday() >= 5:   # skip weekends
                continue
            status = statuses[days_back % len(statuses)]
            att = Attendance(
                employee_id=emp.id,
                date=att_date,
                check_in ="09:00" if status != AttendanceStatus.ABSENT.value else "",
                check_out="18:00" if status in (
                    AttendanceStatus.PRESENT.value, AttendanceStatus.LATE.value
                ) else "",
                status=status,
            )
            db.session.add(att)

    # ── Leaves ────────────────────────────────────────────────────────────────
    leaves_data = [
        (employees[1], LeaveType.ANNUAL.value,  today - timedelta(days=15), today - timedelta(days=13), LeaveStatus.APPROVED.value),
        (employees[2], LeaveType.SICK.value,    today - timedelta(days=5),  today - timedelta(days=3),  LeaveStatus.APPROVED.value),
        (employees[3], LeaveType.ANNUAL.value,  today + timedelta(days=10), today + timedelta(days=15), LeaveStatus.PENDING.value),
        (employees[4], LeaveType.UNPAID.value,  today + timedelta(days=5),  today + timedelta(days=6),  LeaveStatus.REJECTED.value),
        (employees[5], LeaveType.ANNUAL.value,  today + timedelta(days=20), today + timedelta(days=25), LeaveStatus.PENDING.value),
    ]
    for emp, ltype, sdate, edate, lstatus in leaves_data:
        lv = Leave(
            employee_id=emp.id,
            leave_type=ltype,
            start_date=sdate,
            end_date=edate,
            reason="Personal reasons",
            status=lstatus,
            approved_by=employees[0].id if lstatus == LeaveStatus.APPROVED.value else None,
        )
        db.session.add(lv)

    # ── Payroll (current month) ────────────────────────────────────────────────
    for emp in employees:
        pr = Payroll(
            employee_id=emp.id,
            month=today.month,
            year=today.year,
            base_salary=emp.salary,
            allowances=emp.salary * 0.10,
            deductions=emp.salary * 0.05,
            net_pay=emp.salary * 1.05,
            working_days=22,
            present_days=20,
        )
        db.session.add(pr)

    # ── Performance Reviews ────────────────────────────────────────────────────
    ratings  = [5, 4, 3, 5, 4, 3, 4, 5]
    comments = [
        "Exceptional performance, exceeded all targets.",
        "Good work, meets expectations consistently.",
        "Average performance, needs improvement in deadlines.",
        "Outstanding leadership and technical skills.",
        "Creative approach, drives team morale.",
        "Reliable but could improve communication.",
        "Quality-focused, great attention to detail.",
        "Strong financial acumen, key asset to the team.",
    ]
    for i, emp in enumerate(employees):
        pf = Performance(
            employee_id=emp.id,
            reviewer_id=employees[0].id,
            rating=ratings[i],
            comments=comments[i],
            review_date=today - timedelta(days=30),
        )
        db.session.add(pf)

    db.session.commit()
    print("[Seed] Database seeded with demo data successfully.")
