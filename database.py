import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT NOT NULL,
                app_path TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def insert_trigger(self, phrase, app_path):
        self.cursor.execute(
            "INSERT INTO triggers (phrase, app_path) VALUES (?, ?)",
            (phrase, app_path)
        )
        self.connection.commit()

    def fetch_triggers(self):
        self.cursor.execute("SELECT phrase, app_path FROM triggers")
        return self.cursor.fetchall()
