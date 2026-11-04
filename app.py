from datetime import date
from flask import Flask, render_template, redirect, url_for, request
from database import get_db, init_db
app = Flask(__name__)
init_db()

@app.route("/")
def home():
    today = date.today().isoformat()
    conn = get_db()
    habits = conn.execute(
        "SELECT h.id, h.name, EXISTS("
        "SELECT 1 FROM completions c "
        "WHERE c.habit_id = h.id AND c.day = ?) AS done "
        "FROM habits h",
        (today,),
    ).fetchall()
    conn.close()
    return render_template("index.html", habits=habits)

@app.route("/toggle/<int:habit_id>", methods=["POST"])
def toggle(habit_id):
    today = date.today().isoformat()
    conn = get_db()
    exists = conn.execute(
        "SELECT 1 FROM completions WHERE habit_id = ? AND day = ?",
        (habit_id, today),
    ).fetchone()
    if exists:
        conn.execute(
            "DELETE FROM completions WHERE habit_id = ? AND day = ?",
            (habit_id, today),
        )
    else:
        conn.execute(
            "INSERT INTO completions (habit_id, day) VALUES (?, ?)",
            (habit_id, today),
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