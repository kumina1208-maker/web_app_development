"""
app/models/recipe.py
食譜、食材、步驟資料庫 Model — 負責 recipes / ingredients / steps 的 CRUD 操作
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
#  食譜 (recipes) CRUD
# ══════════════════════════════════════════════════════════════

def create(data: dict) -> int | None:
    """
    建立新食譜。

    Args:
        data: 食譜資料字典，必須包含 user_id, title, servings；
              可選包含 description, source_url, image_url,
              prep_time_min, cook_time_min, tags

    Returns:
        int: 新建食譜的 id；發生錯誤時回傳 None
    """
    try:
        now = datetime.utcnow().isoformat()
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO recipes
                (user_id, title, description, source_url, image_url,
                 servings, prep_time_min, cook_time_min, tags,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("user_id"),
                data.get("title"),
                data.get("description"),
                data.get("source_url"),
                data.get("image_url"),
                data.get("servings", 2),
                data.get("prep_time_min"),
                data.get("cook_time_min"),
                data.get("tags"),
                now, now,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Recipe] 建立食譜失敗: {e}")
        return None


def get_all(user_id: int = None) -> list:
    """
    取得所有食譜；若指定 user_id 則僅取該使用者的食譜。

    Args:
        user_id: 使用者 id（可選）

    Returns:
        list[sqlite3.Row]: 食譜列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        if user_id:
            recipes = conn.execute(
                "SELECT * FROM recipes WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        else:
            recipes = conn.execute(
                "SELECT * FROM recipes ORDER BY updated_at DESC"
            ).fetchall()
        conn.close()
        return recipes
    except Exception as e:
        print(f"[Recipe] 取得食譜列表失敗: {e}")
        return []


def get_by_id(recipe_id: int) -> sqlite3.Row | None:
    """
    依 id 查詢單筆食譜。

    Args:
        recipe_id: 食譜 id

    Returns:
        sqlite3.Row: 食譜資料；找不到或錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        recipe = conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
        conn.close()
        return recipe
    except Exception as e:
        print(f"[Recipe] 查詢食譜 id={recipe_id} 失敗: {e}")
        return None


def update(recipe_id: int, data: dict) -> bool:
    """
    更新食譜欄位，自動更新 updated_at。

    Args:
        recipe_id: 食譜 id
        data: 要更新的欄位字典，可包含 title, description, source_url,
              image_url, servings, prep_time_min, cook_time_min, tags

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False
    """
    try:
        allowed = {
            "title", "description", "source_url", "image_url",
            "servings", "prep_time_min", "cook_time_min", "tags",
        }
        fields, values = [], []
        for key, val in data.items():
            if key in allowed:
                fields.append(f"{key} = ?")
                values.append(val)
        if not fields:
            return False
        fields.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(recipe_id)
        conn = get_db_connection()
        conn.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 更新食譜 id={recipe_id} 失敗: {e}")
        return False


def delete(recipe_id: int) -> bool:
    """
    刪除食譜（CASCADE 會一併刪除食材與步驟）。

    Args:
        recipe_id: 食譜 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 刪除食譜 id={recipe_id} 失敗: {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  食材 (ingredients) CRUD
# ══════════════════════════════════════════════════════════════

def add_ingredient(recipe_id: int, name: str, quantity: float, unit: str, notes: str = None) -> int | None:
    """
    新增食材到指定食譜。

    Args:
        recipe_id: 食譜 id
        name: 食材名稱
        quantity: 數量
        unit: 單位
        notes: 備註（可選）

    Returns:
        int: 新建食材的 id；發生錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO ingredients (recipe_id, name, quantity, unit, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (recipe_id, name, quantity, unit, notes),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Recipe] 新增食材失敗: {e}")
        return None


def get_ingredients_by_recipe(recipe_id: int) -> list:
    """
    取得某食譜的所有食材。

    Args:
        recipe_id: 食譜 id

    Returns:
        list[sqlite3.Row]: 食材列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        ingredients = conn.execute(
            "SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,)
        ).fetchall()
        conn.close()
        return ingredients
    except Exception as e:
        print(f"[Recipe] 取得食材列表失敗 (recipe_id={recipe_id}): {e}")
        return []


def update_ingredient(ingredient_id: int, name: str, quantity: float, unit: str, notes: str = None) -> bool:
    """
    更新食材資料。

    Args:
        ingredient_id: 食材 id
        name: 食材名稱
        quantity: 數量
        unit: 單位
        notes: 備註（可選）

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute(
            """
            UPDATE ingredients SET name = ?, quantity = ?, unit = ?, notes = ?
            WHERE id = ?
            """,
            (name, quantity, unit, notes, ingredient_id),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 更新食材 id={ingredient_id} 失敗: {e}")
        return False


def delete_ingredient(ingredient_id: int) -> bool:
    """
    刪除單筆食材。

    Args:
        ingredient_id: 食材 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 刪除食材 id={ingredient_id} 失敗: {e}")
        return False


def delete_ingredients_by_recipe(recipe_id: int) -> bool:
    """
    刪除某食譜的所有食材（用於更新食譜時先清空再重建）。

    Args:
        recipe_id: 食譜 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 清空食材失敗 (recipe_id={recipe_id}): {e}")
        return False


# ══════════════════════════════════════════════════════════════
#  烹飪步驟 (steps) CRUD
# ══════════════════════════════════════════════════════════════

def add_step(recipe_id: int, step_order: int, instruction: str, timer_seconds: int = None) -> int | None:
    """
    新增烹飪步驟到指定食譜。

    Args:
        recipe_id: 食譜 id
        step_order: 步驟順序（1, 2, 3...）
        instruction: 步驟說明
        timer_seconds: 計時秒數（可選）

    Returns:
        int: 新建步驟的 id；發生錯誤時回傳 None
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            """
            INSERT INTO steps (recipe_id, step_order, instruction, timer_seconds)
            VALUES (?, ?, ?, ?)
            """,
            (recipe_id, step_order, instruction, timer_seconds),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except Exception as e:
        print(f"[Recipe] 新增步驟失敗: {e}")
        return None


def get_steps_by_recipe(recipe_id: int) -> list:
    """
    取得某食譜的所有步驟（依 step_order 排序）。

    Args:
        recipe_id: 食譜 id

    Returns:
        list[sqlite3.Row]: 步驟列表；發生錯誤時回傳空列表
    """
    try:
        conn = get_db_connection()
        steps = conn.execute(
            "SELECT * FROM steps WHERE recipe_id = ? ORDER BY step_order ASC",
            (recipe_id,),
        ).fetchall()
        conn.close()
        return steps
    except Exception as e:
        print(f"[Recipe] 取得步驟列表失敗 (recipe_id={recipe_id}): {e}")
        return []


def update_step(step_id: int, instruction: str, timer_seconds: int = None) -> bool:
    """
    更新步驟內容。

    Args:
        step_id: 步驟 id
        instruction: 步驟說明
        timer_seconds: 計時秒數（可選）

    Returns:
        bool: 更新成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute(
            "UPDATE steps SET instruction = ?, timer_seconds = ? WHERE id = ?",
            (instruction, timer_seconds, step_id),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 更新步驟 id={step_id} 失敗: {e}")
        return False


def delete_step(step_id: int) -> bool:
    """
    刪除單筆步驟。

    Args:
        step_id: 步驟 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM steps WHERE id = ?", (step_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 刪除步驟 id={step_id} 失敗: {e}")
        return False


def delete_steps_by_recipe(recipe_id: int) -> bool:
    """
    刪除某食譜的所有步驟（用於更新時先清空再重建）。

    Args:
        recipe_id: 食譜 id

    Returns:
        bool: 刪除成功回傳 True；失敗回傳 False
    """
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM steps WHERE recipe_id = ?", (recipe_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Recipe] 清空步驟失敗 (recipe_id={recipe_id}): {e}")
        return False
