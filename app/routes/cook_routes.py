"""
app/routes/cook_routes.py
下廚模式路由 — 互動式下廚介面與智慧份量轉換
使用 Flask Blueprint 組織路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app.models import recipe as recipe_model

cook_bp = Blueprint("cook", __name__)


# ── 智慧食材份量轉換 ──────────────────────────────────────────
@cook_bp.route("/recipes/<int:id>/scale", methods=["POST"])
def scale_recipe(id):
    """
    智慧食材份量轉換
    - 取得原始食譜與食材
    - 計算比例並換算所有食材用量（不修改資料庫）
    - 渲染 recipes/detail.html 傳入換算後的食材
    """
    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)

    # ── 取得目標份數 ──
    target_servings_str = request.form.get("target_servings", "")
    try:
        target_servings = int(target_servings_str)
        if target_servings < 1:
            raise ValueError
    except ValueError:
        flash("請輸入有效的正整數份數。", "error")
        return redirect(url_for("recipe.recipe_detail", id=id))

    # ── 計算比例並換算食材 ──
    original_servings = recipe["servings"]
    ratio = target_servings / original_servings

    original_ingredients = recipe_model.get_ingredients_by_recipe(id)
    scaled_ingredients = []
    for ing in original_ingredients:
        scaled_ingredients.append({
            "name": ing["name"],
            "quantity": round(ing["quantity"] * ratio, 2),
            "unit": ing["unit"],
            "notes": ing["notes"],
        })

    steps = recipe_model.get_steps_by_recipe(id)

    return render_template(
        "recipes/detail.html",
        recipe=recipe,
        ingredients=scaled_ingredients,
        steps=steps,
        target_servings=target_servings,
    )


# ── 互動式下廚模式 ────────────────────────────────────────────
@cook_bp.route("/recipes/<int:id>/cook", methods=["GET"])
def cook_mode(id):
    """
    進入互動式下廚模式
    - 取得食譜步驟列表（依 step_order 排序）
    - 渲染 recipes/cook.html（前端 JS 負責步驟切換、計時器、Wake Lock）
    """
    recipe = recipe_model.get_by_id(id)
    if not recipe:
        abort(404)

    steps = recipe_model.get_steps_by_recipe(id)

    if not steps:
        flash("此食譜尚無烹飪步驟，無法進入下廚模式。", "error")
        return redirect(url_for("recipe.recipe_detail", id=id))

    return render_template(
        "recipes/cook.html",
        recipe=recipe,
        steps=steps,
    )
