"""
app/routes/recipe_routes.py
食譜路由 — 食譜 CRUD、萬用抓取器、採買清單
使用 Flask Blueprint 組織路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, abort
from app.models import recipe as recipe_model
from app.models import shopping as shopping_model

recipe_bp = Blueprint("recipe", __name__)


# ── 登入檢查輔助函式 ─────────────────────────────────────────
def _require_login():
    """檢查使用者是否已登入，未登入回傳 None 並 flash 提示。"""
    user_id = session.get("user_id")
    if not user_id:
        flash("請先登入。", "error")
    return user_id


# ══════════════════════════════════════════════════════════════
#  食譜 CRUD
# ══════════════════════════════════════════════════════════════

@recipe_bp.route("/recipes/new", methods=["GET"])
def new_recipe_page():
    """顯示新增食譜表單。"""
    if not _require_login():
        return redirect(url_for("main.login_page"))
    return render_template("recipes/new.html")


@recipe_bp.route("/recipes/new", methods=["POST"])
def new_recipe_submit():
    """
    處理新增食譜表單送出
    - 驗證 title / servings 必填
    - 建立食譜 + 食材 + 步驟
    """
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    # ── 取得表單資料 ──
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    servings = request.form.get("servings", "2")
    prep_time_min = request.form.get("prep_time_min", "")
    cook_time_min = request.form.get("cook_time_min", "")
    tags = request.form.get("tags", "").strip()

    # ── 驗證必填欄位 ──
    if not title:
        flash("食譜名稱為必填欄位。", "error")
        return render_template("recipes/new.html")

    try:
        servings = int(servings)
        if servings < 1:
            raise ValueError
    except ValueError:
        flash("份數必須為正整數。", "error")
        return render_template("recipes/new.html")

    # ── 建立食譜 ──
    recipe_data = {
        "user_id": user_id,
        "title": title,
        "description": description or None,
        "servings": servings,
        "prep_time_min": int(prep_time_min) if prep_time_min else None,
        "cook_time_min": int(cook_time_min) if cook_time_min else None,
        "tags": tags or None,
    }
    recipe_id = recipe_model.create(recipe_data)
    if not recipe_id:
        flash("建立食譜失敗，請稍後再試。", "error")
        return render_template("recipes/new.html")

    # ── 新增食材 ──
    ingredient_names = request.form.getlist("ingredient_name[]")
    ingredient_quantities = request.form.getlist("ingredient_quantity[]")
    ingredient_units = request.form.getlist("ingredient_unit[]")
    ingredient_notes = request.form.getlist("ingredient_notes[]")

    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        if not name:
            continue
        try:
            qty = float(ingredient_quantities[i]) if ingredient_quantities[i] else 0
        except (ValueError, IndexError):
            qty = 0
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else ""
        notes = ingredient_notes[i].strip() if i < len(ingredient_notes) else ""
        recipe_model.add_ingredient(recipe_id, name, qty, unit, notes or None)

    # ── 新增步驟 ──
    step_instructions = request.form.getlist("step_instruction[]")
    step_timers = request.form.getlist("step_timer[]")

    for i, instruction in enumerate(step_instructions):
        instruction = instruction.strip()
        if not instruction:
            continue
        try:
            timer = int(step_timers[i]) if i < len(step_timers) and step_timers[i] else None
        except (ValueError, IndexError):
            timer = None
        recipe_model.add_step(recipe_id, i + 1, instruction, timer)

    flash("食譜新增成功！", "success")
    return redirect(url_for("recipe.recipe_detail", id=recipe_id))


@recipe_bp.route("/recipes/<int:id>", methods=["GET"])
def recipe_detail(id):
    """
    食譜詳細頁面
    - 取得食譜、食材、步驟
    - 渲染 recipes/detail.html
    """
    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)

    ingredients = recipe_model.get_ingredients_by_recipe(id)
    steps = recipe_model.get_steps_by_recipe(id)

    return render_template(
        "recipes/detail.html",
        recipe=recipe,
        ingredients=ingredients,
        steps=steps,
    )


@recipe_bp.route("/recipes/<int:id>/edit", methods=["GET"])
def edit_recipe_page(id):
    """顯示編輯食譜表單（預填現有資料）。"""
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != user_id:
        abort(403)

    ingredients = recipe_model.get_ingredients_by_recipe(id)
    steps = recipe_model.get_steps_by_recipe(id)

    return render_template(
        "recipes/edit.html",
        recipe=recipe,
        ingredients=ingredients,
        steps=steps,
    )


@recipe_bp.route("/recipes/<int:id>/edit", methods=["POST"])
def edit_recipe_submit(id):
    """
    處理編輯食譜表單送出
    - 更新主體 + 清空重建食材與步驟
    """
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != user_id:
        abort(403)

    # ── 取得表單資料 ──
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    servings = request.form.get("servings", "2")
    prep_time_min = request.form.get("prep_time_min", "")
    cook_time_min = request.form.get("cook_time_min", "")
    tags = request.form.get("tags", "").strip()

    if not title:
        flash("食譜名稱為必填欄位。", "error")
        return redirect(url_for("recipe.edit_recipe_page", id=id))

    try:
        servings = int(servings)
        if servings < 1:
            raise ValueError
    except ValueError:
        flash("份數必須為正整數。", "error")
        return redirect(url_for("recipe.edit_recipe_page", id=id))

    # ── 更新食譜主體 ──
    update_data = {
        "title": title,
        "description": description or None,
        "servings": servings,
        "prep_time_min": int(prep_time_min) if prep_time_min else None,
        "cook_time_min": int(cook_time_min) if cook_time_min else None,
        "tags": tags or None,
    }
    recipe_model.update(id, update_data)

    # ── 清空並重建食材 ──
    recipe_model.delete_ingredients_by_recipe(id)
    ingredient_names = request.form.getlist("ingredient_name[]")
    ingredient_quantities = request.form.getlist("ingredient_quantity[]")
    ingredient_units = request.form.getlist("ingredient_unit[]")
    ingredient_notes = request.form.getlist("ingredient_notes[]")

    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        if not name:
            continue
        try:
            qty = float(ingredient_quantities[i]) if ingredient_quantities[i] else 0
        except (ValueError, IndexError):
            qty = 0
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else ""
        notes = ingredient_notes[i].strip() if i < len(ingredient_notes) else ""
        recipe_model.add_ingredient(id, name, qty, unit, notes or None)

    # ── 清空並重建步驟 ──
    recipe_model.delete_steps_by_recipe(id)
    step_instructions = request.form.getlist("step_instruction[]")
    step_timers = request.form.getlist("step_timer[]")

    for i, instruction in enumerate(step_instructions):
        instruction = instruction.strip()
        if not instruction:
            continue
        try:
            timer = int(step_timers[i]) if i < len(step_timers) and step_timers[i] else None
        except (ValueError, IndexError):
            timer = None
        recipe_model.add_step(id, i + 1, instruction, timer)

    flash("食譜更新成功！", "success")
    return redirect(url_for("recipe.recipe_detail", id=id))


@recipe_bp.route("/recipes/<int:id>/delete", methods=["POST"])
def delete_recipe(id):
    """
    刪除食譜
    - 驗證食譜存在且屬於目前使用者
    - CASCADE 自動刪除食材與步驟
    """
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != user_id:
        abort(403)

    recipe_model.delete(id)
    flash("食譜已刪除。", "success")
    return redirect(url_for("main.index"))


# ══════════════════════════════════════════════════════════════
#  萬用食譜抓取器
# ══════════════════════════════════════════════════════════════

@recipe_bp.route("/recipes/scrape", methods=["POST"])
def scrape_recipe():
    """
    URL 抓取食譜
    - 呼叫 scraper 解析外部網頁
    - 結果暫存於 Flask session
    """
    if not _require_login():
        return redirect(url_for("main.login_page"))

    url = request.form.get("url", "").strip()
    if not url:
        flash("請輸入食譜網址。", "error")
        return redirect(url_for("recipe.new_recipe_page"))

    try:
        from app.utils.scraper import scrape_recipe as do_scrape
        result = do_scrape(url)
        if not result:
            flash("無法解析此網址，請確認網址正確或改用手動新增。", "error")
            return redirect(url_for("recipe.new_recipe_page"))

        # 暫存到 session
        session["scraped_data"] = result
        return render_template("recipes/preview.html", scraped_data=result)

    except Exception as e:
        flash(f"抓取失敗：{e}", "error")
        return redirect(url_for("recipe.new_recipe_page"))


@recipe_bp.route("/recipes/scrape/confirm", methods=["POST"])
def scrape_confirm():
    """確認儲存抓取結果。"""
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    scraped_data = session.pop("scraped_data", None)
    if not scraped_data:
        flash("沒有暫存的抓取資料。", "error")
        return redirect(url_for("recipe.new_recipe_page"))

    # ── 建立食譜 ──
    recipe_data = {
        "user_id": user_id,
        "title": scraped_data.get("title", "未命名食譜"),
        "description": scraped_data.get("description"),
        "source_url": scraped_data.get("source_url"),
        "servings": scraped_data.get("servings", 2),
    }
    recipe_id = recipe_model.create(recipe_data)
    if not recipe_id:
        flash("儲存食譜失敗。", "error")
        return redirect(url_for("recipe.new_recipe_page"))

    # ── 新增食材 ──
    for ing in scraped_data.get("ingredients", []):
        recipe_model.add_ingredient(
            recipe_id,
            ing.get("name", ""),
            ing.get("quantity", 0),
            ing.get("unit", ""),
            ing.get("notes"),
        )

    # ── 新增步驟 ──
    for i, step in enumerate(scraped_data.get("steps", [])):
        recipe_model.add_step(recipe_id, i + 1, step.get("instruction", ""))

    flash("抓取的食譜已儲存！", "success")
    return redirect(url_for("recipe.recipe_detail", id=recipe_id))


# ══════════════════════════════════════════════════════════════
#  採買清單
# ══════════════════════════════════════════════════════════════

@recipe_bp.route("/shopping-list", methods=["POST"])
def create_shopping_list():
    """
    產生採買清單
    - 取得勾選的食譜 → 彙整食材 → 合併同名食材
    """
    user_id = _require_login()
    if not user_id:
        return redirect(url_for("main.login_page"))

    recipe_ids = request.form.getlist("recipe_ids")
    if not recipe_ids:
        flash("請至少選擇一張食譜。", "error")
        return redirect(url_for("main.index"))

    # ── 建立 session ──
    session_id = shopping_model.create_session(user_id, name="採買清單")
    if not session_id:
        flash("建立採買清單失敗。", "error")
        return redirect(url_for("main.index"))

    # ── 彙整食材 ──
    merged = {}  # key: (name, unit) → total_quantity

    for rid in recipe_ids:
        try:
            rid = int(rid)
        except ValueError:
            continue

        recipe = recipe_model.get_by_id(rid)
        if not recipe:
            continue

        # 關聯食譜到 session（使用原始份數）
        shopping_model.add_recipe_to_session(session_id, rid, recipe["servings"])

        # 取得食材並加總
        ingredients = recipe_model.get_ingredients_by_recipe(rid)
        for ing in ingredients:
            key = (ing["name"], ing["unit"])
            if key in merged:
                merged[key] += ing["quantity"]
            else:
                merged[key] = ing["quantity"]

    # ── 寫入採買項目 ──
    for (name, unit), total_qty in merged.items():
        shopping_model.create_shopping_item(session_id, name, total_qty, unit)

    flash("採買清單已產生！", "success")
    return redirect(url_for("recipe.view_shopping_list", session_id=session_id))


@recipe_bp.route("/shopping-list/<int:session_id>", methods=["GET"])
def view_shopping_list(session_id):
    """檢視採買清單。"""
    session_data = shopping_model.get_session_by_id(session_id)
    if not session_data:
        abort(404)

    items = shopping_model.get_items_by_session(session_id)
    return render_template(
        "shopping/list.html",
        session_data=session_data,
        items=items,
    )


@recipe_bp.route("/shopping-list/toggle/<int:item_id>", methods=["POST"])
def toggle_shopping_item(item_id):
    """標記食材已購買 / 取消購買。"""
    success = shopping_model.toggle_purchased(item_id)
    if success:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "error"}), 500
