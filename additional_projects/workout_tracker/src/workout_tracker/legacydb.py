from pathlib import Path
import sqlite3

DB_PATH = Path.home() / ".workout_tracker.sqlite3"
SCHEMA = (
    "CREATE TABLE IF NOT EXISTS logs("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "date TEXT, exercise TEXT, weight REAL, reps INTEGER);"
)

def get_conn():
    c = sqlite3.connect(DB_PATH)
    c.execute(SCHEMA)
    return c

def insert_log(date, exercise, weight, reps):
    with get_conn() as c:
        c.execute(
            "INSERT INTO logs(date,exercise,weight,reps) VALUES (?,?,?,?)",
            (date, exercise, weight, reps),
        )

def fetch_logs(exercise, limit=None):
    with get_conn() as c:
        cur = c.execute(
            "SELECT date,weight,reps FROM logs WHERE exercise=? ORDER BY date",
            (exercise,),
        )
        rows = cur.fetchall()
    return rows[-limit:] if limit else rows

def delete_log(row_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM logs WHERE id=?", (row_id,))

def fetch_logs_with_id(exercise: str, limit: int | None = None):
    with get_conn() as conn:
        q = "SELECT id, date, weight, reps FROM logs WHERE exercise=? ORDER BY date"
        rows = conn.execute(q, (exercise,)).fetchall()
    return rows[-limit:] if limit else rows

