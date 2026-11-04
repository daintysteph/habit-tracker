from datetime import date, timedelta
from flask import Flask, render_template, redirect, url_for, request
from database import get_db, init_db

app = Flask(__name__)
init_db()

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

@app.route("/")
def home():
    today = date.today()
    week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    conn = get_db()
    habits = []
    for h in conn.execute("SELECT * FROM habits").fetchall():
        rows = conn.execute(
            "SELECT day FROM completions WHERE habit_id = ?", (h["id"],)
        ).fetchall()
        done_days = {row["day"] for row in rows}
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
    return render_template("index.html", habits=habits)

@app.route("/toggle/<int:habit_id>/<day>", methods=["POST"])
def toggle(habit_id, day):
    try:
        parsed = date.fromisoformat(day)
    except ValueError:
        return redirect(url_for("home"))
    if parsed > date.today():
        return redirect(url_for("home"))
    conn = get_db()
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
def add():
    name = request.form["name"].strip()
    if name:
        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO habits (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect(url_for("home"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete(habit_id):
    conn = get_db()
    conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)