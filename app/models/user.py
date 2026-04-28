"""
app/models/user.py
使用者資料庫 Model — 負責 users 資料表的 CRUD 操作
使用 Python 內建 sqlite3 模組
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


def _get_db(db_path: str = "instance/database.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── Create ────────────────────────────────────────────────────
def create_user(username: str, email: str, password: str) -> int:
    """建立新使用者，密碼自動雜湊後儲存。回傳新 user 的 id。"""
    password_hash = generate_password_hash(password)
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


# ── Read ──────────────────────────────────────────────────────
def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    """依 id 查詢使用者，找不到回傳 None。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    """依 email 查詢使用者，用於登入驗證。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """依 username 查詢使用者，用於重複性檢查。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def verify_password(email: str, password: str) -> sqlite3.Row | None:
    """驗證 email + 密碼，成功回傳使用者 Row，失敗回傳 None。"""
    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


# ── Update ────────────────────────────────────────────────────
def update_user(user_id: int, username: str = None, email: str = None) -> bool:
    """更新使用者資料（username / email），回傳是否成功。"""
    fields, values = [], []
    if username:
        fields.append("username = ?")
        values.append(username)
    if email:
        fields.append("email = ?")
        values.append(email)
    if not fields:
        return False
    values.append(user_id)
    with _get_db() as conn:
        conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values
        )
        conn.commit()
    return True


# ── Delete ────────────────────────────────────────────────────
def delete_user(user_id: int) -> bool:
    """刪除使用者（CASCADE 會一併刪除其食譜與採買清單）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return True
