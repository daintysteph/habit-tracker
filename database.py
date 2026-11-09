import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DEFAULT_HABITS = ["Exercise", "Reading", "Swimming", "Eating fruits"]

def get_db():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id SERIAL PRIMARY KEY, "
        "username TEXT NOT NULL UNIQUE, "
        "password_hash TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS habits ("
        "id SERIAL PRIMARY KEY, "
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
            "INSERT INTO habits (user_id, name) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (user_id, name),
        )