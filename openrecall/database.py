import sqlite3
from collections import namedtuple
from typing import Any, List

from openrecall.config import db_path

Entry = namedtuple("Entry", ["id", "app", "title", "text", "timestamp", "embedding"])


def create_db() -> None:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS entries
               (id INTEGER PRIMARY KEY AUTOINCREMENT, app TEXT, title TEXT, text TEXT, timestamp INTEGER, embedding BLOB)"""
        )
        conn.commit()


def get_all_entries() -> List[Entry]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute("SELECT * FROM entries").fetchall()
        return [Entry(*result) for result in results]


def get_timestamps() -> List[int]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute(
            "SELECT timestamp FROM entries ORDER BY timestamp DESC"
        ).fetchall()
        return [result[0] for result in results]


def insert_entry(
    text: str, timestamp: int, embedding: Any, app: str, title: str
) -> None:
    embedding_bytes = embedding.tobytes()
    try:

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO entries (text, timestamp, embedding, app, title) VALUES (?, ?, ?, ?, ?)",
                (text, timestamp, embedding_bytes, app, title),
            )
            conn.commit()
    except sqlite3.OperationalError as e:
        print("Error inserting entry:", e)


def get_entries_by_time_range(start_time: int, end_time: int) -> List[Entry]:
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        results = c.execute(
            "SELECT * FROM entries WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC",
            (start_time, end_time),
        ).fetchall()
        return [Entry(*result) for result in results]
