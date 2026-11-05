import sqlite3

DEFAULT_HABITS = ["Exercise", "Reading", "Water", "Food"]

def get_db():
    conn = sqlite3.connect("habits.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT NOT NULL UNIQUE, "
        "password_hash TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS habits ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER NOT NULL, "
        "name TEXT NOT NULL, "
        "UNIQUE (user_id, name))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS completions ("
        "habit_id INTEGER NOT NULL, "
        "day TEXT NOT NULL, "
        "PRIMARY KEY (habit_id, day))"
    )
    conn.commit()
    conn.close()

def add_default_habits(conn, user_id):
    for name in DEFAULT_HABITS:
        conn.execute(
            "INSERT OR IGNORE INTO habits (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )