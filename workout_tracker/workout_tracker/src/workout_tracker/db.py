from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

PACKAGE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = PACKAGE_DIR.parent / "instance"
LEGACY_DB_PATH = INSTANCE_DIR / "widget_logs.sqlite3"


def _ensure_legacy_db() -> None:
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(LEGACY_DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                exercise TEXT NOT NULL,
                weight REAL NOT NULL,
                reps INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def get_conn() -> sqlite3.Connection:
    _ensure_legacy_db()
    conn = sqlite3.connect(LEGACY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert_log(date: str, exercise: str, weight: float, reps: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO logs (date, exercise, weight, reps) VALUES (?, ?, ?, ?)",
            (date, exercise, float(weight), int(reps)),
        )
        conn.commit()


def fetch_logs(exercise: str, limit: int | None = 10) -> list[tuple[str, float, int]]:
    with get_conn() as conn:
        if limit:
            cur = conn.execute(
                """
                SELECT date, weight, reps
                FROM logs
                WHERE exercise = ?
                ORDER BY date, id
                LIMIT ?
                """,
                (exercise, int(limit)),
            )
        else:
            cur = conn.execute(
                """
                SELECT date, weight, reps
                FROM logs
                WHERE exercise = ?
                ORDER BY date, id
                """,
                (exercise,),
            )
        return [(row[0], row[1], row[2]) for row in cur.fetchall()]


def fetch_logs_with_id(exercise: str, limit: int | None = 10) -> list[tuple[int, str, float, int]]:
    with get_conn() as conn:
        if limit:
            cur = conn.execute(
                """
                SELECT id, date, weight, reps
                FROM logs
                WHERE exercise = ?
                ORDER BY date DESC, id DESC
                LIMIT ?
                """,
                (exercise, int(limit)),
            )
        else:
            cur = conn.execute(
                """
                SELECT id, date, weight, reps
                FROM logs
                WHERE exercise = ?
                ORDER BY date DESC, id DESC
                """,
                (exercise,),
            )
        return [(row[0], row[1], row[2], row[3]) for row in cur.fetchall()]


def delete_log(log_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM logs WHERE id = ?", (int(log_id),))
        conn.commit()
