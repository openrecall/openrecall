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
            "SELECT timestamp FROM entries ORDER BY timestamp DESC LIMIT 1000"
        ).fetchall()
        return [result[0] for result in results]


def insert_entry(
    text: str, timestamp: int, embedding: Any, app: str, title: str
) -> None:
    embedding_bytes = embedding.tobytes()
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO entries (text, timestamp, embedding, app, title) VALUES (?, ?, ?, ?, ?)",
            (text, timestamp, embedding_bytes, app, title),
        )
        conn.commit()
