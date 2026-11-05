import os
import sqlite3
from datetime import date, timedelta
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db, add_default_habits

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
init_db()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def get_streak(conn, habit_id):
    rows = conn.execute(
        "SELECT day FROM completions WHERE habit_id = ?", (habit_id,)
    ).fetchall()
    days = {row["day"] for row in rows}
    current = date.today()
    if current.isoformat() not in days:
        current -= timedelta(days=1)
    streak = 0
    while current.isoformat() in days:
        streak += 1
        current -= timedelta(days=1)
    return streak

def owns_habit(conn, habit_id):
    row = conn.execute(
        "SELECT 1 FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, session["user_id"]),
    ).fetchone()
    return row is not None

@app.route("/")
@login_required
def home():
    today = date.today()
    week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    conn = get_db()
    user = conn.execute(
        "SELECT username FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    if user is None:
        conn.close()
        session.clear()
        return redirect(url_for("login"))
    habits = []
    rows = conn.execute(
        "SELECT * FROM habits WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    for h in rows:
        done_rows = conn.execute(
            "SELECT day FROM completions WHERE habit_id = ?", (h["id"],)
        ).fetchall()
        done_days = {row["day"] for row in done_rows}
        habits.append({
            "id": h["id"],
            "name": h["name"],
            "streak": get_streak(conn, h["id"]),
            "days": [
                {
                    "iso": d.isoformat(),
                    "label": "Today" if d == today else d.strftime("%a"),
                    "done": d.isoformat() in done_days,
                }
                for d in week
            ],
        })
    conn.close()
    return render_template("index.html", habits=habits, username=user["username"])

@app.route("/toggle/<int:habit_id>/<day>", methods=["POST"])
@login_required
def toggle(habit_id, day):
    try:
        parsed = date.fromisoformat(day)
    except ValueError:
        return redirect(url_for("home"))
    if parsed > date.today():
        return redirect(url_for("home"))
    conn = get_db()
    if not owns_habit(conn, habit_id):
        conn.close()
        return redirect(url_for("home"))
    exists = conn.execute(
        "SELECT 1 FROM completions WHERE habit_id = ? AND day = ?",
        (habit_id, day),
    ).fetchone()
    if exists:
        conn.execute(
            "DELETE FROM completions WHERE habit_id = ? AND day = ?",
            (habit_id, day),
        )
    else:
        conn.execute(
            "INSERT INTO completions (habit_id, day) VALUES (?, ?)",
            (habit_id, day),
        )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form["name"].strip()
    if name:
        conn = get_db()
        conn.execute(
            "INSERT OR IGNORE INTO habits (user_id, name) VALUES (?, ?)",
            (session["user_id"], name),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("home"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
@login_required
def delete(habit_id):
    conn = get_db()
    if owns_habit(conn, habit_id):
        conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or len(password) < 6:
            flash("Enter a username and a password of at least 6 characters.")
        else:
            conn = get_db()
            try:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                add_default_habits(conn, cur.lastrowid)
                conn.commit()
                session["user_id"] = cur.lastrowid
                return redirect(url_for("home"))
            except sqlite3.IntegrityError:
                flash("That username is taken.")
            finally:
                conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("home"))
        flash("Wrong username or password.")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)