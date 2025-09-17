import sqlite3
import threading
from typing import List, Optional

DB_NAME = "users.db"
_lock = threading.Lock()

def _conn():
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)

def init_db():
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS banned (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

def add_user(user_id: int, username: Optional[str]):
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username or ""))
        conn.commit()
        conn.close()

def get_all_users() -> List[int]:
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        users = [row[0] for row in cur.fetchall()]
        conn.close()
        return users

def is_banned(user_id: int) -> bool:
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM banned WHERE user_id = ?", (user_id,))
        banned = cur.fetchone() is not None
        conn.close()
        return banned

def ban_user(user_id: int, reason: str = ""):
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO banned (user_id, reason) VALUES (?, ?)", (user_id, reason))
        conn.commit()
        conn.close()

def unban_user(user_id: int):
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM banned WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

def record_message(user_id: int, message: str):
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
        conn.commit()
        conn.close()

def count_messages_last_minute(user_id: int) -> int:
    with _lock:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM messages
            WHERE user_id = ?
              AND created_at >= datetime('now', '-1 minutes')
        """, (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

