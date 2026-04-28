"""
app.py
食譜收藏系統 — 應用程式入口點
"""

from app import create_app, init_db

app = create_app()

if __name__ == "__main__":
    # 首次執行時自動初始化資料庫
    import os
    db_path = app.config["DATABASE"]
    if not os.path.exists(db_path):
        with app.app_context():
            app.init_db()

    app.run(debug=True, host="0.0.0.0", port=5000)
