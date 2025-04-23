import unittest
import sqlite3
import os
import tempfile
import time
import numpy as np
from unittest.mock import patch

# Temporarily adjust path to import from openrecall
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import from openrecall.database, mocking db_path *before* the import
# Create a temporary file path that will be used by the mock
temp_db_file = tempfile.NamedTemporaryFile(delete=False)
mock_db_path = temp_db_file.name
temp_db_file.close() # Close the file handle, but the file persists because delete=False

with patch('openrecall.config.db_path', mock_db_path):
    from openrecall.database import (
        create_db,
        insert_entry,
        get_all_entries,
        get_timestamps,
        Entry,
    )
    # Also patch db_path within the database module itself if it was imported directly there
    import openrecall.database
    openrecall.database.db_path = mock_db_path


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary database file for all tests in this class."""
        # The database path is already patched by the module-level patch
        cls.db_path = mock_db_path
        # Ensure the database and table are created once
        create_db()

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database file after all tests."""
        # Try closing connection if any test left it open (though setUp/tearDown should handle this)
        try:
            if hasattr(cls, 'conn') and cls.conn:
                cls.conn.close()
        except Exception:
            pass # Ignore errors during cleanup
        os.remove(cls.db_path)
        # Clean up sys.path modification
        sys.path.pop(0)


    def setUp(self):
        """Connect to the database and clear entries before each test."""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM entries")
        self.conn.commit()
        # No need to close here, will be handled by tearDown or next setUp potentially

    def tearDown(self):
        """Close the database connection after each test."""
        if self.conn:
            self.conn.close()

    def test_create_db(self):
        """Test if create_db creates the table and index."""
        # Check if table exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entries'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'entries')

        # Check if index exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_timestamp'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'idx_timestamp')

    def test_02_insert_entry(self):
        """Test inserting a single entry."""
        ts = int(time.time())
        embedding = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        inserted_id = insert_entry("Test text", ts, embedding, "TestApp", "TestTitle")

        self.assertIsNotNone(inserted_id)
        self.assertIsInstance(inserted_id, int)

        # Verify the entry exists in the DB
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (inserted_id,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        # (id, app, title, text, timestamp, embedding_blob)
        self.assertEqual(result[1], "TestApp")
        self.assertEqual(result[2], "TestTitle")
        self.assertEqual(result[3], "Test text")
        self.assertEqual(result[4], ts)
        retrieved_embedding = np.frombuffer(result[5], dtype=np.float32)
        np.testing.assert_array_almost_equal(retrieved_embedding, embedding)

    def test_insert_duplicate_timestamp(self):
        """Test inserting an entry with a duplicate timestamp (should be ignored)."""
        ts = int(time.time())
        embedding1 = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        embedding2 = np.array([0.4, 0.5, 0.6], dtype=np.float32)

        id1 = insert_entry("First text", ts, embedding1, "App1", "Title1")
        self.assertIsNotNone(id1)

        # Try inserting another entry with the same timestamp
        id2 = insert_entry("Second text", ts, embedding2, "App2", "Title2")
        self.assertIsNone(id2, "Inserting duplicate timestamp should return None")

        # Verify only the first entry exists
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entries WHERE timestamp = ?", (ts,))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

        cursor.execute("SELECT text FROM entries WHERE timestamp = ?", (ts,))
        text = cursor.fetchone()[0]
        self.assertEqual(text, "First text") # Ensure the first one was kept

    def test_get_all_entries_empty(self):
        """Test getting entries from an empty database."""
        entries = get_all_entries()
        self.assertEqual(entries, [])

    def test_get_all_entries_multiple(self):
        """Test retrieving multiple entries."""
        ts1 = int(time.time())
        ts2 = ts1 + 10
        ts3 = ts1 - 10 # Ensure ordering works
        emb1 = np.array([0.1] * 5, dtype=np.float32)
        emb2 = np.array([0.2] * 5, dtype=np.float32)
        emb3 = np.array([0.3] * 5, dtype=np.float32)

        insert_entry("Text 1", ts1, emb1, "App1", "Title1")
        insert_entry("Text 2", ts2, emb2, "App2", "Title2")
        insert_entry("Text 3", ts3, emb3, "App3", "Title3")

        entries = get_all_entries()
        self.assertEqual(len(entries), 3)

        # Entries should be ordered by timestamp DESC
        self.assertEqual(entries[0].timestamp, ts2)
        self.assertEqual(entries[0].text, "Text 2")
        self.assertEqual(entries[0].app, "App2")
        self.assertEqual(entries[0].title, "Title2")
        np.testing.assert_array_almost_equal(entries[0].embedding, emb2)
        self.assertIsInstance(entries[0].id, int)

        self.assertEqual(entries[1].timestamp, ts1)
        self.assertEqual(entries[1].text, "Text 1")
        np.testing.assert_array_almost_equal(entries[1].embedding, emb1)

        self.assertEqual(entries[2].timestamp, ts3)
        self.assertEqual(entries[2].text, "Text 3")
        np.testing.assert_array_almost_equal(entries[2].embedding, emb3)

    def test_get_timestamps_empty(self):
        """Test getting timestamps from an empty database."""
        timestamps = get_timestamps()
        self.assertEqual(timestamps, [])

    def test_get_timestamps_multiple(self):
        """Test retrieving multiple timestamps."""
        ts1 = int(time.time())
        ts2 = ts1 + 10
        ts3 = ts1 - 10
        emb = np.array([0.1] * 5, dtype=np.float32) # Embedding content doesn't matter here

        insert_entry("T1", ts1, emb, "A1", "T1")
        insert_entry("T2", ts2, emb, "A2", "T2")
        insert_entry("T3", ts3, emb, "A3", "T3")

        timestamps = get_timestamps()
        self.assertEqual(len(timestamps), 3)
        # Timestamps should be ordered DESC
        self.assertEqual(timestamps, [ts2, ts1, ts3])


if __name__ == '__main__':
    unittest.main()