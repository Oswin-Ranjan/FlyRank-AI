import sqlite3

DB_NAME = "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )
    """)

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # Insert sample tasks only once
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks(title, done) VALUES (?, ?)",
            [
                ("Complete this assignment", 0),
                ("Write README", 0),
                ("Push to GitHub", 1)
            ]
        )

    conn.commit()
    conn.close()