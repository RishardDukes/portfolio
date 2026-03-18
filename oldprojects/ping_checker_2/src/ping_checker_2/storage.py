from pathlib import Path
import sqlite3
from datetime import datetime
DB_PATH = Path.home() / ".ping_checker.sqlite3"
SCHEMA = "CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, host TEXT, ok INTEGER, latency_ms REAL);"
def conn():
    c = sqlite3.connect(DB_PATH); c.execute(SCHEMA); return c
def record(host, ok, latency_ms):
    with conn() as c:
        c.execute("INSERT INTO checks(ts,host,ok,latency_ms) VALUES (?,?,?,?)",
                  (datetime.utcnow().isoformat(), host, 1 if ok else 0, latency_ms))
def get_history():
    with conn() as c:
        return c.execute("SELECT ts,host,ok,latency_ms FROM checks ORDER BY ts").fetchall()
