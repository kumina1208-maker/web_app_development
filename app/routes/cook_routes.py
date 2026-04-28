"""
app/routes/cook_routes.py
下廚模式路由 — 互動式下廚介面與智慧份量轉換
"""

from flask import Blueprint, render_template, request, redirect, url_for, abort

cook_bp = Blueprint("cook", __name__)


# ── 智慧食材份量轉換 ──────────────────────────────────────────
@cook_bp.route("/recipes/<int:id>/scale", methods=["POST"])
def scale_recipe(id):
    """
    智慧食材份量轉換
    - 輸入：表單欄位 target_servings（目標份數）
    - 取得原始食譜與食材
    - 計算比例 ratio = target_servings / original_servings
    - 逐一乘以 ratio 得到換算後的食材用量（不修改資料庫）
    - 渲染 recipes/detail.html，傳入換算後的食材資料
    - 錯誤處理：目標份數非正整數 → flash 錯誤訊息
    """
    pass


# ── 互動式下廚模式 ────────────────────────────────────────────
@cook_bp.route("/recipes/<int:id>/cook", methods=["GET"])
def cook_mode(id):
    """
    進入互動式下廚模式
    - 取得食譜步驟列表（依 step_order 排序）
    - 傳入步驟數量、每步計時資訊
    - 渲染 recipes/cook.html
      - 前端 JS 負責：步驟放大檢視、進度指示器、Wake Lock 螢幕常亮
    - 找不到食譜 → 404
    """
    pass
