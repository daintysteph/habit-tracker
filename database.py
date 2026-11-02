import sqlite3

def get_db():
       conn = sqlite3.connect("habits.db")
       conn.row_factory = sqlite3.Row
       return conn

def init_db():
       conn = get_db()
       conn.execute(
           "CREATE TABLE IF NOT EXISTS habits ("
           "id INTEGER PRIMARY KEY AUTOINCREMENT, "
           "name TEXT NOT NULL UNIQUE)"
       )
       conn.execute(
           "CREATE TABLE IF NOT EXISTS completions ("
           "habit_id INTEGER NOT NULL, "
           "day TEXT NOT NULL, "
           "PRIMARY KEY (habit_id, day))"
       )
       for name in ["Exercise", "Reading", "Water", "Food"]:
           conn.execute(
               "INSERT OR IGNORE INTO habits (name) VALUES (?)", (name,))
       conn.commit()
       conn.close()

if __name__ == "__main__":
       init_db()
       conn = get_db()
       for row in conn.execute("SELECT * FROM habits"):
           print(row["id"], row["name"])
       conn.close()
