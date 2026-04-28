"""
app/routes/main_routes.py
基礎路由 — 首頁、使用者註冊、登入、登出
使用 Flask Blueprint 組織路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import user as user_model
from app.models import recipe as recipe_model

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
    user_id = session.get("user_id")

    # 取得食譜列表
    if user_id:
        recipes = recipe_model.get_all(user_id=user_id)
    else:
        recipes = recipe_model.get_all()

    # 搜尋篩選
    q = request.args.get("q", "").strip()
    if q:
        recipes = [r for r in recipes if q.lower() in r["title"].lower()]

    return render_template("index.html", recipes=recipes, q=q)


# ── 註冊 ──────────────────────────────────────────────────────
@main_bp.route("/register", methods=["GET"])
def register_page():
    """顯示註冊表單頁面。"""
    return render_template("register.html")


@main_bp.route("/register", methods=["POST"])
def register_submit():
    """
    處理註冊表單送出
    - 驗證欄位非空、密碼一致
    - 檢查 username / email 無重複
    - 呼叫 user_model.create_user() 建立帳號
    """
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")

    # ── 輸入驗證 ──
    if not username or not email or not password:
        flash("請填寫所有必填欄位。", "error")
        return render_template("register.html")

    if password != password_confirm:
        flash("兩次輸入的密碼不一致。", "error")
        return render_template("register.html")

    if len(password) < 4:
        flash("密碼長度至少需要 4 個字元。", "error")
        return render_template("register.html")

    # ── 重複檢查 ──
    if user_model.get_user_by_username(username):
        flash("此使用者名稱已被使用。", "error")
        return render_template("register.html")

    if user_model.get_user_by_email(email):
        flash("此電子郵件已被註冊。", "error")
        return render_template("register.html")

    # ── 建立帳號 ──
    new_id = user_model.create_user(username, email, password)
    if new_id:
        flash("註冊成功！請登入。", "success")
        return redirect(url_for("main.login_page"))
    else:
        flash("註冊失敗，請稍後再試。", "error")
        return render_template("register.html")


# ── 登入 ──────────────────────────────────────────────────────
@main_bp.route("/login", methods=["GET"])
def login_page():
    """顯示登入表單頁面。"""
    return render_template("login.html")


@main_bp.route("/login", methods=["POST"])
def login_submit():
    """
    處理登入表單送出
    - 呼叫 user_model.verify_password() 驗證
    - 成功 → 寫入 Flask session，重導向 /
    """
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("請填寫電子郵件與密碼。", "error")
        return render_template("login.html")

    user = user_model.verify_password(email, password)
    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash(f"歡迎回來，{user['username']}！", "success")
        return redirect(url_for("main.index"))
    else:
        flash("電子郵件或密碼錯誤。", "error")
        return render_template("login.html")


# ── 登出 ──────────────────────────────────────────────────────
@main_bp.route("/logout", methods=["GET"])
def logout():
    """清除 Flask session 並重導向首頁。"""
    session.clear()
    flash("已成功登出。", "success")
    return redirect(url_for("main.index"))
