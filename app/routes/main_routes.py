"""
app/routes/main_routes.py
基礎路由 — 首頁、使用者註冊、登入、登出
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

main_bp = Blueprint("main", __name__)


# ── 首頁 ──────────────────────────────────────────────────────
@main_bp.route("/", methods=["GET"])
def index():
    """
    首頁 - 食譜列表
    - 取得目前使用者的所有食譜
    - 支援 ?q= 關鍵字搜尋
    - 渲染 index.html
    """
    pass


# ── 註冊 ──────────────────────────────────────────────────────
@main_bp.route("/register", methods=["GET"])
def register_page():
    """
    顯示註冊表單頁面
    - 渲染 register.html
    """
    pass


@main_bp.route("/register", methods=["POST"])
def register_submit():
    """
    處理註冊表單送出
    - 輸入：username, email, password, password_confirm
    - 驗證欄位非空、密碼一致、email 格式
    - 檢查 username / email 無重複
    - 呼叫 user.create_user() 建立帳號
    - 成功 → 重導向 /login
    - 失敗 → 重新渲染 register.html 附帶錯誤訊息
    """
    pass


# ── 登入 ──────────────────────────────────────────────────────
@main_bp.route("/login", methods=["GET"])
def login_page():
    """
    顯示登入表單頁面
    - 渲染 login.html
    """
    pass


@main_bp.route("/login", methods=["POST"])
def login_submit():
    """
    處理登入表單送出
    - 輸入：email, password
    - 呼叫 user.verify_password() 驗證
    - 成功 → 寫入 Flask session，重導向 /
    - 失敗 → 重新渲染 login.html 附帶錯誤訊息
    """
    pass


# ── 登出 ──────────────────────────────────────────────────────
@main_bp.route("/logout", methods=["GET"])
def logout():
    """
    登出
    - 清除 Flask session
    - 重導向 /
    """
    pass
