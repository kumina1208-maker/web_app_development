"""
app/models/shopping.py
採買工作階段與清單項目 Model — 負責 shopping_sessions / shopping_session_recipes / shopping_items 的 CRUD 操作
使用 Python 內建 sqlite3 模組，資料庫路徑為 instance/database.db
"""

import sqlite3
from datetime import datetime


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


# ══════════════════════════════════════════════════════════════
#  採買工作階段 (shopping_sessions) CRUD
# ══════════════════════════════════════════════════════════════

def create_session(user_id: int, name: str = None) -> int | None:
    """
    建立新的採買工作階段。

    Args:
        user_id: 使用者 id
        name: 採買清單名稱（可選，如「本週採購」）

    Returns:
        int: 新建工作階段的 id；發生錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO shopping_sessions (user_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, name, datetime.utcnow().isoformat()),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Shopping] 建立採買工作階段失敗: {e}")
        return None


def get_session_by_id(session_id: int) -> sqlite3.Row | None:
    """
    依 id 查詢單筆採買工作階段。

    Args:
        session_id: 工作階段 id

    Returns:
        sqlite3.Row: 工作階段資料；找不到或錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        session = conn.execute(
            "SELECT * FROM shopping_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        conn.close()
        return session
    except Exception as e:
        print(f"[Shopping] 查詢工作階段 id={session_id} 失敗: {e}")
        return None


def get_all_sessions(user_id: int) -> list:
    """
    取得使用者的所有採買工作階段。

    Args:
        user_id: 使用者 id

    Returns:
        list[sqlite3.Row]: 工作階段列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        sessions = conn.execute(
            "SELECT * FROM shopping_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        conn.close()
        return sessions
    except Exception as e:
        print(f"[Shopping] 取得工作階段列表失敗: {e}")
        return []


def delete_session(session_id: int) -> bool:
    """
    刪除採買工作階段（CASCADE 會一併刪除關聯食譜與項目）。

    Args:
        session_id: 工作階段 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM shopping_sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Shopping] 刪除工作階段 id={session_id} 失敗: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  採買工作階段 × 食譜 關聯 (shopping_session_recipes)
# ══════════════════════════════════════════════════════════════

def add_recipe_to_session(session_id: int, recipe_id: int, scaled_servings: int) -> int | None:
    """
    將食譜加入採買工作階段。

    Args:
        session_id: 工作階段 id
        recipe_id: 食譜 id
        scaled_servings: 此次採買所需份數

    Returns:
        int: 新建關聯的 id；發生錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO shopping_session_recipes (session_id, recipe_id, scaled_servings)
            VALUES (?, ?, ?)
            """,
            (session_id, recipe_id, scaled_servings),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Shopping] 加入食譜到工作階段失敗: {e}")
        return None


def get_recipes_in_session(session_id: int) -> list:
    """
    取得某採買工作階段所包含的所有食譜及其份數。

    Args:
        session_id: 工作階段 id

    Returns:
        list[sqlite3.Row]: 食譜關聯列表（含 title 與 original_servings）；
                           發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        records = conn.execute(
            """
            SELECT ssr.*, r.title, r.servings AS original_servings
            FROM shopping_session_recipes ssr
            JOIN recipes r ON ssr.recipe_id = r.id
            WHERE ssr.session_id = ?
            """,
            (session_id,),
        ).fetchall()
        conn.close()
        return records
    except Exception as e:
        print(f"[Shopping] 取得工作階段食譜失敗 (session_id={session_id}): {e}")
        return []


# ══════════════════════════════════════════════════════════════
#  採買清單食材項目 (shopping_items) CRUD
# ══════════════════════════════════════════════════════════════

def create_shopping_item(session_id: int, ingredient_name: str, total_quantity: float, unit: str) -> int | None:
    """
    建立採買清單中的一筆食材項目。

    Args:
        session_id: 工作階段 id
        ingredient_name: 食材名稱
        total_quantity: 彙整後的總用量
        unit: 單位

    Returns:
        int: 新建項目的 id；發生錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO shopping_items
                (session_id, ingredient_name, total_quantity, unit, is_purchased, updated_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (session_id, ingredient_name, total_quantity, unit, datetime.utcnow().isoformat()),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Shopping] 建立採買項目失敗: {e}")
        return None


def get_items_by_session(session_id: int) -> list:
    """
    取得某採買工作階段的所有食材項目。

    Args:
        session_id: 工作階段 id

    Returns:
        list[sqlite3.Row]: 食材項目列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        items = conn.execute(
            "SELECT * FROM shopping_items WHERE session_id = ? ORDER BY ingredient_name ASC",
            (session_id,),
        ).fetchall()
        conn.close()
        return items
    except Exception as e:
        print(f"[Shopping] 取得採買項目失敗 (session_id={session_id}): {e}")
        return []


def toggle_purchased(item_id: int) -> bool:
    """
    切換食材的已購買狀態（0 ↔ 1）。

    Args:
        item_id: 食材項目 id

    Returns:
        bool: 切換成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute(
            """
            UPDATE shopping_items
            SET is_purchased = CASE WHEN is_purchased = 0 THEN 1 ELSE 0 END,
                updated_at = ?
            WHERE id = ?
            """,
            (datetime.utcnow().isoformat(), item_id),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Shopping] 切換購買狀態失敗 (item_id={item_id}): {e}")
        return False


def delete_items_by_session(session_id: int) -> bool:
    """
    刪除某工作階段的所有食材項目（用於重新產生清單時先清空）。

    Args:
        session_id: 工作階段 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM shopping_items WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Shopping] 清空採買項目失敗 (session_id={session_id}): {e}")
        return False
