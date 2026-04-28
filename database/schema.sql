-- 食譜收藏系統 - SQLite Schema
-- 建立順序需遵守 FK 依賴：users → recipes → ingredients/steps → shopping_sessions → ...

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 使用者
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    DATETIME DEFAULT (datetime('now'))
);

-- ============================================================
-- 2. 食譜
-- ============================================================
CREATE TABLE IF NOT EXISTS recipes (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    title          TEXT    NOT NULL,
    description    TEXT,
    source_url     TEXT,
    image_url      TEXT,
    servings       INTEGER NOT NULL DEFAULT 2,
    prep_time_min  INTEGER,
    cook_time_min  INTEGER,
    tags           TEXT,
    created_at     DATETIME DEFAULT (datetime('now')),
    updated_at     DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 3. 食材（屬於食譜）
-- ============================================================
CREATE TABLE IF NOT EXISTS ingredients (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id  INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    quantity   REAL    NOT NULL DEFAULT 0,
    unit       TEXT    NOT NULL DEFAULT '',
    notes      TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- ============================================================
-- 4. 烹飪步驟（屬於食譜）
-- ============================================================
CREATE TABLE IF NOT EXISTS steps (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id      INTEGER NOT NULL,
    step_order     INTEGER NOT NULL,
    instruction    TEXT    NOT NULL,
    timer_seconds  INTEGER,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- ============================================================
-- 5. 採買工作階段
-- ============================================================
CREATE TABLE IF NOT EXISTS shopping_sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT,
    created_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- 6. 採買工作階段 × 食譜 關聯（多對多）
-- ============================================================
CREATE TABLE IF NOT EXISTS shopping_session_recipes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER NOT NULL,
    recipe_id        INTEGER NOT NULL,
    scaled_servings  INTEGER NOT NULL DEFAULT 2,
    FOREIGN KEY (session_id) REFERENCES shopping_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id)  REFERENCES recipes(id)           ON DELETE CASCADE
);

-- ============================================================
-- 7. 採買清單食材項目（由後端彙整產生）
-- ============================================================
CREATE TABLE IF NOT EXISTS shopping_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       INTEGER NOT NULL,
    ingredient_name  TEXT    NOT NULL,
    total_quantity   REAL    NOT NULL DEFAULT 0,
    unit             TEXT    NOT NULL DEFAULT '',
    is_purchased     INTEGER NOT NULL DEFAULT 0,  -- 0 = 未購買, 1 = 已購買
    updated_at       DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES shopping_sessions(id) ON DELETE CASCADE
);
