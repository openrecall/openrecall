import sqlite3
from openrecall.config import db_path

#Test database structure
def test_db_structure (tmp_path):
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                """PRAGMA TABLE_INFO (entries)"""
            )
            columns = c.fetchall()
            assert (columns==[(0, 'id', 'INTEGER', 0, None, 1)
                              , (1, 'app', 'TEXT', 0, None, 0)
                              , (2, 'title', 'TEXT', 0, None, 0)
                              , (3, 'text', 'TEXT', 0, None, 0)
                              , (4, 'timestamp', 'INTEGER', 0, None, 0)
                              , (5, 'embedding', 'BLOB', 0, None, 0)
                              ])
