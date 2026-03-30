import json
import sqlite3
from dcss.constants import DATABASE_PATH

"""CREATE TABLE messages (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   to TEXT,
                   data TEXT,
                   timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                   )"""

"""Initializing database to store data received from microcontrollers

Creates an SQLite database and sets up the `messages` table
if it does not already exist.

`id`automatically increments key
`recipient` details who the message is for
`data` stores sensor readings as a JSON string
`timestamp` records when the row of data was added
"""


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


"""Logging data to database

Function that when called inserts a row of data into the database

Args:
    to (str): string of the intended recipient of the data
    data (dict): data dictionary that will be converted to a JSON string

Returns:
    None
"""


def log_message(to: str, data: dict) -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (recipient, data) VALUES (?, ?)",
            (to, json.dumps(data)),
        )

        conn.commit()
