"""
app/models/recipe.py
食譜、食材、步驟資料庫 Model — 負責 recipes / ingredients / steps 的 CRUD 操作
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
#  食譜 (recipes) CRUD
# ══════════════════════════════════════════════════════════════

def create_recipe(
    user_id: int,
    title: str,
    servings: int,
    description: str = None,
    source_url: str = None,
    image_url: str = None,
    prep_time_min: int = None,
    cook_time_min: int = None,
    tags: str = None,
) -> int:
    """建立新食譜，回傳新 recipe 的 id。"""
    now = datetime.utcnow().isoformat()
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO recipes
                (user_id, title, description, source_url, image_url,
                 servings, prep_time_min, cook_time_min, tags,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id, title, description, source_url, image_url,
                servings, prep_time_min, cook_time_min, tags,
                now, now,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_recipes(user_id: int = None) -> list[sqlite3.Row]:
    """取得所有食譜；若指定 user_id 則僅取該使用者的食譜。"""
    with _get_db() as conn:
        if user_id:
            return conn.execute(
                "SELECT * FROM recipes WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        return conn.execute(
            "SELECT * FROM recipes ORDER BY updated_at DESC"
        ).fetchall()


def get_recipe_by_id(recipe_id: int) -> sqlite3.Row | None:
    """依 id 查詢單筆食譜。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()


def update_recipe(recipe_id: int, **kwargs) -> bool:
    """更新食譜欄位（傳入欄位名稱=新值），自動更新 updated_at。"""
    allowed = {
        "title", "description", "source_url", "image_url",
        "servings", "prep_time_min", "cook_time_min", "tags",
    }
    fields, values = [], []
    for key, val in kwargs.items():
        if key in allowed:
            fields.append(f"{key} = ?")
            values.append(val)
    if not fields:
        return False
    fields.append("updated_at = ?")
    values.append(datetime.utcnow().isoformat())
    values.append(recipe_id)
    with _get_db() as conn:
        conn.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        conn.commit()
    return True


def delete_recipe(recipe_id: int) -> bool:
    """刪除食譜（CASCADE 會一併刪除食材與步驟）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
    return True


# ══════════════════════════════════════════════════════════════
#  食材 (ingredients) CRUD
# ══════════════════════════════════════════════════════════════

def add_ingredient(recipe_id: int, name: str, quantity: float, unit: str, notes: str = None) -> int:
    """新增食材到指定食譜，回傳新 ingredient 的 id。"""
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO ingredients (recipe_id, name, quantity, unit, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (recipe_id, name, quantity, unit, notes),
        )
        conn.commit()
        return cursor.lastrowid


def get_ingredients_by_recipe(recipe_id: int) -> list[sqlite3.Row]:
    """取得某食譜的所有食材。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,)
        ).fetchall()


def update_ingredient(ingredient_id: int, name: str, quantity: float, unit: str, notes: str = None) -> bool:
    """更新食材資料。"""
    with _get_db() as conn:
        conn.execute(
            """
            UPDATE ingredients SET name = ?, quantity = ?, unit = ?, notes = ?
            WHERE id = ?
            """,
            (name, quantity, unit, notes, ingredient_id),
        )
        conn.commit()
    return True


def delete_ingredient(ingredient_id: int) -> bool:
    """刪除單筆食材。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
        conn.commit()
    return True


def delete_ingredients_by_recipe(recipe_id: int) -> bool:
    """刪除某食譜的所有食材（用於更新食譜時先清空再重建）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        conn.commit()
    return True


# ══════════════════════════════════════════════════════════════
#  烹飪步驟 (steps) CRUD
# ══════════════════════════════════════════════════════════════

def add_step(recipe_id: int, step_order: int, instruction: str, timer_seconds: int = None) -> int:
    """新增烹飪步驟到指定食譜，回傳新 step 的 id。"""
    with _get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO steps (recipe_id, step_order, instruction, timer_seconds)
            VALUES (?, ?, ?, ?)
            """,
            (recipe_id, step_order, instruction, timer_seconds),
        )
        conn.commit()
        return cursor.lastrowid


def get_steps_by_recipe(recipe_id: int) -> list[sqlite3.Row]:
    """取得某食譜的所有步驟（依 step_order 排序）。"""
    with _get_db() as conn:
        return conn.execute(
            "SELECT * FROM steps WHERE recipe_id = ? ORDER BY step_order ASC",
            (recipe_id,),
        ).fetchall()


def update_step(step_id: int, instruction: str, timer_seconds: int = None) -> bool:
    """更新步驟內容。"""
    with _get_db() as conn:
        conn.execute(
            "UPDATE steps SET instruction = ?, timer_seconds = ? WHERE id = ?",
            (instruction, timer_seconds, step_id),
        )
        conn.commit()
    return True


def delete_step(step_id: int) -> bool:
    """刪除單筆步驟。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM steps WHERE id = ?", (step_id,))
        conn.commit()
    return True


def delete_steps_by_recipe(recipe_id: int) -> bool:
    """刪除某食譜的所有步驟（用於更新時先清空再重建）。"""
    with _get_db() as conn:
        conn.execute("DELETE FROM steps WHERE recipe_id = ?", (recipe_id,))
        conn.commit()
    return True
