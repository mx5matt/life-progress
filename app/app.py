import os
import sqlite3
import calendar
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "life-progress-local-v010")
DB = os.environ.get("LIFE_PROGRESS_DB", "/data/life-progress.db")


@contextmanager
def db():
    conn = sqlite3.connect(DB, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            lifespan INTEGER NOT NULL DEFAULT 85
        );

        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            relationship TEXT,
            birth_date TEXT NOT NULL,
            milestone_age INTEGER
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            target_date TEXT NOT NULL,
            notes TEXT
        );
        """)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def anniversary_for_year(month, day, year):
    day = min(day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def full_years(start, end):
    years = end.year - start.year
    anniversary = anniversary_for_year(start.month, start.day, end.year)
    if end < anniversary:
        years -= 1
    return max(years, 0)


def full_months(start, end):
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def christmases_until(target, today):
    if target <= today:
        return 0
    year = today.year
    count = 0
    while year <= target.year:
        christmas = date(year, 12, 25)
        if today < christmas <= target:
            count += 1
        year += 1
    return count


def weekends_until(target, today):
    if target <= today:
        return 0
    days = (target - today).days
    full_weeks, extra = divmod(days, 7)
    count = full_weeks
    for offset in range(1, extra + 1):
        if (today + timedelta(days=offset)).weekday() == 5:
            count += 1
    return count


def countdown(target, today=None):
    today = today or date.today()
    days = (target - today).days
    future_days = max(days, 0)
    return {
        "days": future_days,
        "weeks": future_days // 7,
        "months": full_months(today, target) if target > today else 0,
        "years": full_years(today, target) if target > today else 0,
        "weekends": weekends_until(target, today),
        "christmases": christmases_until(target, today),
        "past": days < 0,
        "today": days == 0,
    }


def profile_stats(profile):
    today = date.today()
    birth = parse_date(profile["birth_date"])
    lifespan = profile["lifespan"]
    target = anniversary_for_year(birth.month, birth.day, birth.year + lifespan)

    lived_days = max((today - birth).days, 0)
    total_days = max((target - birth).days, 1)
    remaining_days = max((target - today).days, 0)

    year_start = date(today.year, 1, 1)
    year_end = date(today.year + 1, 1, 1)
    year_elapsed = (today - year_start).days
    year_total = (year_end - year_start).days

    total_weeks = max(total_days // 7, 1)
    lived_weeks = min(lived_days // 7, total_weeks)

    return {
        "today": today,
        "birth": birth,
        "age": full_years(birth, today),
        "lived_days": lived_days,
        "lived_weeks": lived_days // 7,
        "lived_months": full_months(birth, today),
        "target": target,
        "remaining_days": remaining_days,
        "remaining_weeks": remaining_days // 7,
        "life_percent": min((lived_days / total_days) * 100, 100),
        "year_percent": (year_elapsed / year_total) * 100,
        "total_weeks": total_weeks,
        "completed_weeks": lived_weeks,
        "current_week": min(lived_weeks, total_weeks - 1),
    }


@app.before_request
def ensure_db():
    init_db()


@app.get("/health")
def health():
    with db() as conn:
        conn.execute("SELECT 1").fetchone()
    return jsonify(status="ok", version="0.1.0")


@app.route("/")
def index():
    with db() as conn:
        profile = conn.execute("SELECT * FROM profile WHERE id=1").fetchone()
        people = conn.execute("SELECT * FROM people ORDER BY birth_date").fetchall()
        milestones = conn.execute(
            "SELECT * FROM milestones ORDER BY target_date"
        ).fetchall()

    if not profile:
        return redirect(url_for("setup"))

    stats = profile_stats(profile)

    people_view = []
    for person in people:
        row = dict(person)
        birth = parse_date(row["birth_date"])
        row["age"] = full_years(birth, date.today())
        if row["milestone_age"] is not None:
            target = anniversary_for_year(
                birth.month, birth.day, birth.year + row["milestone_age"]
            )
            row["target"] = target
            row["countdown"] = countdown(target)
        people_view.append(row)

    milestone_view = []
    for milestone in milestones:
        row = dict(milestone)
        target = parse_date(row["target_date"])
        row["target"] = target
        row["countdown"] = countdown(target)
        milestone_view.append(row)

    return render_template(
        "index.html",
        profile=profile,
        stats=stats,
        people=people_view,
        milestones=milestone_view,
    )


@app.route("/setup", methods=["GET", "POST"])
def setup():
    with db() as conn:
        profile = conn.execute("SELECT * FROM profile WHERE id=1").fetchone()

    if request.method == "POST":
        name = request.form["name"].strip()
        birth_date = request.form["birth_date"]
        lifespan = int(request.form.get("lifespan", 85))

        if not name or lifespan < 1 or lifespan > 150:
            flash("Please enter a valid name and lifespan.")
            return redirect(url_for("setup"))

        parse_date(birth_date)

        with db() as conn:
            conn.execute(
                """
                INSERT INTO profile(id,name,birth_date,lifespan)
                VALUES(1,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    birth_date=excluded.birth_date,
                    lifespan=excluded.lifespan
                """,
                (name, birth_date, lifespan),
            )
        return redirect(url_for("index"))

    return render_template("setup.html", profile=profile)


@app.post("/people")
def add_person():
    name = request.form["name"].strip()
    relationship = request.form.get("relationship", "").strip()
    birth_date = request.form["birth_date"]
    milestone_raw = request.form.get("milestone_age", "").strip()
    milestone_age = int(milestone_raw) if milestone_raw else None
    parse_date(birth_date)

    with db() as conn:
        conn.execute(
            """
            INSERT INTO people(name,relationship,birth_date,milestone_age)
            VALUES(?,?,?,?)
            """,
            (name, relationship, birth_date, milestone_age),
        )
    return redirect(url_for("index"))


@app.post("/people/<int:person_id>/delete")
def delete_person(person_id):
    with db() as conn:
        conn.execute("DELETE FROM people WHERE id=?", (person_id,))
    return redirect(url_for("index"))


@app.post("/milestones")
def add_milestone():
    title = request.form["title"].strip()
    target_date = request.form["target_date"]
    notes = request.form.get("notes", "").strip()
    parse_date(target_date)

    with db() as conn:
        conn.execute(
            "INSERT INTO milestones(title,target_date,notes) VALUES(?,?,?)",
            (title, target_date, notes),
        )
    return redirect(url_for("index"))


@app.post("/milestones/<int:milestone_id>/delete")
def delete_milestone(milestone_id):
    with db() as conn:
        conn.execute("DELETE FROM milestones WHERE id=?", (milestone_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
