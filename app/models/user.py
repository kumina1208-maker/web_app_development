"""
app/models/user.py
使用者資料庫 Model — 負責 users 資料表的 CRUD 操作
使用 Python 內建 sqlite3 模組，資料庫路徑為 instance/database.db
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


def get_db_connection(db_path: str = "instance/database.db"):
    """
    取得 SQLite 資料庫連線。

    Args:
        db_path: 資料庫檔案路徑，預設為 instance/database.db

    Returns:
        sqlite3.Connection: 資料庫連線物件，row_factory 設為 sqlite3.Row
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── Create ────────────────────────────────────────────────────

def create_user(username: str, email: str, password: str) -> int | None:
    """
    建立新使用者，密碼自動雜湊後儲存。

    Args:
        username: 使用者名稱（唯一）
        email: 電子郵件（唯一）
        password: 明文密碼（會自動雜湊）

    Returns:
        int: 新建使用者的 id；發生錯誤時回傳 None
    """
    try:
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (username, email, password_hash, datetime.utcnow().isoformat()),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.IntegrityError as e:
        print(f"[User] 建立使用者失敗（重複資料）: {e}")
        return None
    except Exception as e:
        print(f"[User] 建立使用者時發生未預期錯誤: {e}")
        return None


# ── Read ──────────────────────────────────────────────────────

def get_all() -> list:
    """
    取得所有使用者。

    Returns:
        list[sqlite3.Row]: 所有使用者的列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"[User] 取得所有使用者失敗: {e}")
        return []


def get_by_id(user_id: int) -> sqlite3.Row | None:
    """
    依 id 查詢單筆使用者。

    Args:
        user_id: 使用者 id

    Returns:
        sqlite3.Row: 使用者資料；找不到或錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"[User] 查詢使用者 id={user_id} 失敗: {e}")
        return None


def get_user_by_email(email: str) -> sqlite3.Row | None:
    """
    依 email 查詢使用者，用於登入驗證。

    Args:
        email: 電子郵件

    Returns:
        sqlite3.Row: 使用者資料；找不到或錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"[User] 查詢 email={email} 失敗: {e}")
        return None


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """
    依 username 查詢使用者，用於重複性檢查。

    Args:
        username: 使用者名稱

    Returns:
        sqlite3.Row: 使用者資料；找不到或錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"[User] 查詢 username={username} 失敗: {e}")
        return None


def verify_password(email: str, password: str) -> sqlite3.Row | None:
    """
    驗證 email + 密碼是否正確。

    Args:
        email: 電子郵件
        password: 明文密碼

    Returns:
        sqlite3.Row: 驗證成功回傳使用者資料；失敗回傳 None
    """
    try:
        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None
    except Exception as e:
        print(f"[User] 密碼驗證失敗: {e}")
        return None


# ── Update ────────────────────────────────────────────────────

def update(user_id: int, data: dict) -> bool:
    """
    更新使用者資料。

    Args:
        user_id: 使用者 id
        data: 要更新的欄位字典，可包含 username, email

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False
    """
    try:
        allowed = {"username", "email"}
        fields, values = [], []
        for key, val in data.items():
            if key in allowed and val is not None:
                fields.append(f"{key} = ?")
                values.append(val)
        if not fields:
            return False
        values.append(user_id)
        conn = get_db_connection()
        conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print(f"[User] 更新使用者 id={user_id} 失敗（重複資料）: {e}")
        return False
    except Exception as e:
        print(f"[User] 更新使用者 id={user_id} 時發生未預期錯誤: {e}")
        return False


# ── Delete ────────────────────────────────────────────────────

def delete(user_id: int) -> bool:
    """
    刪除使用者（CASCADE 會一併刪除其食譜與採買清單）。

    Args:
        user_id: 使用者 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[User] 刪除使用者 id={user_id} 失敗: {e}")
        return False
