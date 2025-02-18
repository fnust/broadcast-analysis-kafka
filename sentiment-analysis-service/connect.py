import sqlite3
import time

import numpy as np


def calculate_weighted_sentiment(
    sentiment, subscribers, likes=0, replies=0, base_influence=0.1
):
    likes_max = 30
    replies_max = 5
    subscribers_max = 1000

    weight_likes = 0.8
    weight_replies = 0.2

    likes_norm = np.log1p(likes) / np.log1p(likes_max)
    replies_norm = np.log1p(replies) / np.log1p(replies_max)
    subscribers_norm = np.log1p(subscribers) / np.log1p(subscribers_max)

    weighted_sentiment = sentiment * (
        weight_likes
        * (likes_norm + base_influence)
        * (subscribers_norm + base_influence)
        + weight_replies
        * (replies_norm + base_influence)
        * (subscribers_norm + base_influence)
    )

    return weighted_sentiment


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

    def insert_record(self, score, subscribers, timestamp):
        weighted_sentiment = calculate_weighted_sentiment(score, subscribers)
        self.cursor.execute(
            """
            INSERT INTO comments (score, subscribers, timestamp, weighted_score) VALUES (?, ?, ?, ?)
        """,
            (score, subscribers, timestamp, weighted_sentiment),
        )
        self.conn.commit()

    def get_current_data(self):
        current_time = int(time.time())
        two_minutes_ago = current_time - 60 * 2

        self.cursor.execute(
            """
            SELECT weighted_score FROM comments 
            WHERE timestamp >= ?
            """,
            (two_minutes_ago,),
        )
        scores = self.cursor.fetchall()
        comment_count = len(scores)

        if scores:
            average_score = sum(score[0] for score in scores) / comment_count
            return {"semantic_score": average_score, "comment_count": comment_count}
        else:
            return {"semantic_score": 0, "comment_count": 0}

    def increment_likes(self, comment_id):
        self.cursor.execute(
            """
        SELECT likes, subscribers, score, replies FROM comments WHERE id = ?
        """,
            (comment_id,),
        )

        result = self.cursor.fetchone()
        if result:
            likes, subscribers, score, replies = result
            weighted_sentiment = calculate_weighted_sentiment(
                score, subscribers, likes + 1, replies
            )

            self.cursor.execute(
                """
                UPDATE comments
                SET likes = likes + 1, weighted_score = ?
                WHERE id = ?
            """,
                (weighted_sentiment, comment_id),
            )
            self.conn.commit()

    def increment_replies(self, comment_id):
        self.cursor.execute(
            """
        SELECT likes, subscribers, score, replies FROM comments WHERE id = ?
        """,
            (comment_id,),
        )

        result = self.cursor.fetchone()
        if result:
            likes, subscribers, score, replies = result
            weighted_sentiment = calculate_weighted_sentiment(
                score, subscribers, likes, replies + 1
            )

            self.cursor.execute(
                """
                UPDATE comments
                SET replies = replies + 1, weighted_score = ?
                WHERE id = ?
            """,
                (weighted_sentiment, comment_id),
            )
            self.conn.commit()

    def close(self):
        self.conn.close()
