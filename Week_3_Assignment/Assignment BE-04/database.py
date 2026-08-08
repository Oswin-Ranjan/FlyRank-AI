import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        done BOOLEAN NOT NULL DEFAULT FALSE
    )
    """)

    cursor.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO tasks(title, done)
            VALUES (%s, %s)
            """,
            [
                ("Complete this assignment", False),
                ("Write README", False),
                ("Push to GitHub", True),
            ],
        )

    conn.commit()
    conn.close()