"""
app/__init__.py
Flask 應用程式工廠與初始化設定
"""

import os
import sqlite3
from flask import Flask


def create_app():
    """建立並設定 Flask 應用程式實例。"""
    app = Flask(__name__)

    # ── 基礎設定 ──────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", os.path.join(app.instance_path, "database.db"))

    # 確保 instance 資料夾存在
    os.makedirs(app.instance_path, exist_ok=True)

    # ── 資料庫初始化 ──────────────────────────────────────────
    def get_db():
        """取得資料庫連線（每次請求共用同一連線）。"""
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    app.get_db = get_db

    def init_db():
        """讀取 schema.sql 建立資料表。"""
        db = get_db()
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.close()
        print("[OK] Database initialized successfully!")

    app.init_db = init_db

    # ── 註冊 Blueprints ──────────────────────────────────────
    from app.routes.main_routes import main_bp
    from app.routes.recipe_routes import recipe_bp
    from app.routes.cook_routes import cook_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(cook_bp)

    return app


def init_db():
    """供外部呼叫的資料庫初始化函式。"""
    app = create_app()
    with app.app_context():
        app.init_db()
