import sqlite3

from openrecall.config import db_path


def create_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS entries
           (id INTEGER PRIMARY KEY AUTOINCREMENT, app TEXT, title TEXT, text TEXT, timestamp INTEGER, embedding BLOB)"""
    )
    conn.commit()
    conn.close()


def get_all_entries():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    results = c.execute("SELECT * FROM entries").fetchall()
    conn.close()
    entries = []
    for result in results:
        entries.append(
            {
                "id": result[0],
                "app": result[1],
                "title": result[2],
                "text": result[3],
                "timestamp": result[4],
                "embedding": result[5],
            }
        )
    return entries


def get_timestamps():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    results = c.execute(
        "SELECT timestamp FROM entries ORDER BY timestamp DESC LIMIT 1000"
    ).fetchall()
    timestamps = [result[0] for result in results]
    conn.close()
    return timestamps

def insert_entry(text, timestamp, embedding, app, title):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    embedding_bytes = embedding.tobytes()
    c.execute(
        "INSERT INTO entries (text, timestamp, embedding, app, title) VALUES (?, ?, ?, ?, ?)",
        (
            text,
            timestamp,
            embedding_bytes,
            app,
            title,
        ),
    )
    conn.commit()
    conn.close()
