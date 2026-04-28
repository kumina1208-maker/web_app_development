"""
app/models/shopping.py
採買工作階段與清單項目 Model — 負責 shopping_sessions / shopping_session_recipes / shopping_items 的 CRUD 操作
使用 Python 內建 sqlite3 模組
"""

import sqlite3
from datetime import datetime


def _get_db(db_path: str = "instance/database.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ══════════════════════════════════════════════════════════════
#  採買工作階段 (shopping_sessions)
# ══════════════════════════════════════════════════════════════

def create_session(user_id: int, name: str = None) -> int:
    """建立新的採買工作階段，回傳 session_id。"""
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO shopping_sessions (user_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, name, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


def get_session_by_id(session_id: int) -> sqlite3.Row | None:
    """依 id 查詢單筆採買工作階段。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM shopping_sessions WHERE id = ?", (session_id,)
        ).fetchone()


def get_sessions_by_user(user_id: int) -> list[sqlite3.Row]:
    """取得使用者的所有採買工作階段。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM shopping_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()


def delete_session(session_id: int) -> bool:
    """刪除採買工作階段（CASCADE 會一併刪除關聯食譜與項目）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM shopping_sessions WHERE id = ?", (session_id,))
        conn.commit()
    return True


# ══════════════════════════════════════════════════════════════
#  採買工作階段 × 食譜 關聯 (shopping_session_recipes)
# ══════════════════════════════════════════════════════════════

def add_recipe_to_session(session_id: int, recipe_id: int, scaled_servings: int) -> int:
    """將食譜加入採買工作階段，回傳關聯 id。"""
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO shopping_session_recipes (session_id, recipe_id, scaled_servings)
            VALUES (?, ?, ?)
            """,
            (session_id, recipe_id, scaled_servings),
        )
        conn.commit()
        return cursor.lastrowid


def get_recipes_in_session(session_id: int) -> list[sqlite3.Row]:
    """取得某採買工作階段所包含的所有食譜及其份數。"""
    with _get_db() as conn:
        return conn.execute(
            """
            SELECT ssr.*, r.title, r.servings AS original_servings
            FROM shopping_session_recipes ssr
            JOIN recipes r ON ssr.recipe_id = r.id
            WHERE ssr.session_id = ?
            """,
            (session_id,),
        ).fetchall()


# ══════════════════════════════════════════════════════════════
#  採買清單食材項目 (shopping_items)
# ══════════════════════════════════════════════════════════════

def create_shopping_item(
    session_id: int,
    ingredient_name: str,
    total_quantity: float,
    unit: str,
) -> int:
    """建立採買清單中的一筆食材項目，回傳 item_id。"""
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO shopping_items
                (session_id, ingredient_name, total_quantity, unit, is_purchased, updated_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (session_id, ingredient_name, total_quantity, unit, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cursor.lastrowid


def get_items_by_session(session_id: int) -> list[sqlite3.Row]:
    """取得某採買工作階段的所有食材項目。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM shopping_items WHERE session_id = ? ORDER BY ingredient_name ASC",
            (session_id,),
        ).fetchall()


def toggle_purchased(item_id: int) -> bool:
    """切換食材的已購買狀態（0 ↔ 1）。"""
    with _get_db() as conn:
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
    return True


def delete_items_by_session(session_id: int) -> bool:
    """刪除某工作階段的所有食材項目（用於重新產生清單時先清空）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM shopping_items WHERE session_id = ?", (session_id,))
        conn.commit()
    return True
