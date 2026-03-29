import json
import sqlite3
from DCSS.constants import DATABASE_PATH

"""CREATE TABLE messages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   to TEXT,
                   data TEXT,
                   timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                   )"""


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                data TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )


def log_message(to: str, data: dict) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (recipient, data) VALUES (?, ?)",
            (to, json.dumps(data)),
        )

        conn.commit()
