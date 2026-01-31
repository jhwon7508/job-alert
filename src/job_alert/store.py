import sqlite3
from datetime import datetime
import os

class JobStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seen_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    source TEXT,
                    first_seen_at TIMESTAMP
                )
            """)
            conn.commit()

    def is_seen(self, url: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM seen_posts WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def mark_seen(self, url: str, title: str, source: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO seen_posts (url, title, source, first_seen_at)
                VALUES (?, ?, ?, ?)
            """, (url, title, source, datetime.now().isoformat()))
            conn.commit()
