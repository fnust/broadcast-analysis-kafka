import random
import sqlite3


class CommentDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score REAL NOT NULL,
        subscribers INTEGER NOT NULL DEFAULT 0,
        likes INTEGER NOT NULL DEFAULT 0,
        replies INTEGER NOT NULL DEFAULT 0,
        timestamp INTEGER,
        weighted_score REAL DEFAULT 0
        )
        """)
        self.conn.commit()

    def get_random_comment_id(self):
        self.cursor.execute("SELECT COUNT(*) FROM comments")
        count = self.cursor.fetchone()[0]

        if count == 0:
            return None
        random_index = random.randint(0, count - 1)

        self.cursor.execute("SELECT id FROM comments LIMIT 1 OFFSET ?", (random_index,))
        random_id = self.cursor.fetchone()

        return {"comment_id": random_id[0]} if random_id else None

    def close(self):
        self.conn.close()
