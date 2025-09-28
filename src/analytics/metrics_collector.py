from datetime import datetime
import sqlite3

class MetricsCollector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.create_metrics_table()

    def create_metrics_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_role TEXT,
                    query TEXT,
                    response_time REAL,
                    success INTEGER
                )
            ''')

    def log_interaction(self, user_role, query, response_time, success):
        timestamp = datetime.now().isoformat()
        with self.connection:
            self.connection.execute('''
                INSERT INTO metrics (timestamp, user_role, query, response_time, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, user_role, query, response_time, success))

    def close(self):
        self.connection.close()