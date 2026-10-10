"""A small durable event register."""
import sqlite3


class EventStore:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        with self.connection:
            self.connection.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, amount INTEGER NOT NULL)")

    def record(self, event_id, amount):
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event id must be a nonblank string")
        if type(amount) is not int or not 1 <= amount <= 2**63 - 1:
            raise ValueError("amount must be a positive signed 64-bit integer")
        with self.connection:
            cursor = self.connection.execute("INSERT OR IGNORE INTO events (id, amount) VALUES (?, ?)", (event_id, amount))
        return cursor.rowcount == 1

    def entries(self):
        return self.connection.execute("SELECT id, amount FROM events ORDER BY id").fetchall()

    def close(self):
        self.connection.close()
