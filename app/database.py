import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("APP_DB_PATH", str(DB_DIR / "app.db")))


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Alice", "alice@example.com"),
            )
            conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Bob", "bob@example.com"),
            )

        post_count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        if post_count == 0:
            conn.execute(
                "INSERT INTO posts (title, body, user_id) VALUES (?, ?, ?)",
                ("First post", "Hello from SQLite", 1),
            )
            conn.execute(
                "INSERT INTO posts (title, body, user_id) VALUES (?, ?, ?)",
                ("Second post", "FastAPI + SQL practice", 1),
            )
            conn.execute(
                "INSERT INTO posts (title, body, user_id) VALUES (?, ?, ?)",
                ("Another post", "Learning SQL syntax", 2),
            )

        conn.commit()


init_db()
