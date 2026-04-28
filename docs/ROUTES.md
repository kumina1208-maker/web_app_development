# 食譜收藏系統 - 路由設計文件

本文件依據 `PRD.md`、`ARCHITECTURE.md` 與 `DB_DESIGN.md` 設計，規劃每個頁面的 URL 路徑、HTTP 方法、對應模板與處理邏輯。

---

## 1. 路由總覽表格

### 基礎路由 (`main_routes.py`)

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|----------|---------|---------|------|
| 首頁 / 食譜列表 | GET | `/` | `index.html` | 顯示所有食譜卡片，支援搜尋 |
| 註冊頁面 | GET | `/register` | `register.html` | 顯示註冊表單 |
| 送出註冊 | POST | `/register` | — | 建立使用者並重導向登入頁 |
| 登入頁面 | GET | `/login` | `login.html` | 顯示登入表單 |
| 送出登入 | POST | `/login` | — | 驗證後重導向首頁 |
| 登出 | GET | `/logout` | — | 清除 session 並重導向首頁 |

### 食譜路由 (`recipe_routes.py`)

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|----------|---------|---------|------|
| 新增食譜頁面 | GET | `/recipes/new` | `recipes/new.html` | 顯示空白新增表單 |
| 送出新增食譜 | POST | `/recipes/new` | — | 儲存食譜並重導向詳細頁 |
| 食譜詳細頁面 | GET | `/recipes/<id>` | `recipes/detail.html` | 顯示食譜完整內容 |
| 編輯食譜頁面 | GET | `/recipes/<id>/edit` | `recipes/edit.html` | 顯示預填編輯表單 |
| 送出編輯食譜 | POST | `/recipes/<id>/edit` | — | 更新並重導向詳細頁 |
| 刪除食譜 | POST | `/recipes/<id>/delete` | — | 刪除並重導向首頁 |
| URL 抓取食譜 | POST | `/recipes/scrape` | `recipes/preview.html` | 解析網址並預覽結果 |
| 確認儲存抓取結果 | POST | `/recipes/scrape/confirm` | — | 儲存並重導向詳細頁 |

### 下廚模式路由 (`cook_routes.py`)

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|----------|---------|---------|------|
| 份量換算 | POST | `/recipes/<id>/scale` | `recipes/detail.html` | 換算後重新渲染詳細頁 |
| 進入下廚模式 | GET | `/recipes/<id>/cook` | `recipes/cook.html` | 互動式下廚介面 |

### 採買清單路由 (`recipe_routes.py`)

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|------|----------|---------|---------|------|
| 產生採買清單 | POST | `/shopping-list` | `shopping/list.html` | 勾選多張食譜後彙整顯示 |
| 採買清單詳細 | GET | `/shopping-list/<session_id>` | `shopping/list.html` | 檢視已建立的採買清單 |
| 標記食材已購買 | POST | `/shopping-list/toggle/<item_id>` | — | 切換購買狀態，回傳 200 |

---

## 2. 每個路由的詳細說明

### 2-1. `GET /` — 首頁 / 食譜列表

- **輸入**：Query string `?q=關鍵字`（可選，用於搜尋食譜名稱）
- **處理邏輯**：
  1. 取得目前登入使用者的 `user_id`（若未登入則顯示所有公開食譜或引導登入）
  2. 呼叫 `recipe.get_all_recipes(user_id)` 取得食譜列表
  3. 若有搜尋關鍵字則進行篩選
- **輸出**：渲染 `index.html`，傳入食譜列表
- **錯誤處理**：無特殊錯誤情境

### 2-2. `GET /register` / `POST /register` — 使用者註冊

- **輸入**（POST）：表單欄位 `username`, `email`, `password`, `password_confirm`
- **處理邏輯**：
  1. 驗證欄位非空、密碼一致、email 格式
  2. 檢查 `user.get_user_by_email()` 與 `user.get_user_by_username()` 無重複
  3. 呼叫 `user.create_user()` 建立帳號
- **輸出**：成功 → 重導向 `/login`；失敗 → 重新渲染 `register.html` 附帶錯誤訊息
- **錯誤處理**：欄位驗證失敗、帳號/信箱重複

### 2-3. `GET /login` / `POST /login` — 使用者登入

- **輸入**（POST）：表單欄位 `email`, `password`
- **處理邏輯**：
  1. 呼叫 `user.verify_password(email, password)` 驗證
  2. 驗證成功寫入 Flask `session`
- **輸出**：成功 → 重導向 `/`；失敗 → 重新渲染 `login.html` 附帶錯誤訊息
- **錯誤處理**：帳密錯誤

### 2-4. `GET /recipes/new` / `POST /recipes/new` — 新增食譜

- **輸入**（POST）：表單欄位 `title`, `description`, `servings`, `prep_time_min`, `cook_time_min`, `tags`, 以及動態食材列表 `ingredients[][name/quantity/unit/notes]`、步驟列表 `steps[][instruction/timer_seconds]`
- **處理邏輯**：
  1. 表單驗證（title 與 servings 必填）
  2. 呼叫 `recipe.create_recipe()` 建立食譜
  3. 迴圈呼叫 `recipe.add_ingredient()` 與 `recipe.add_step()` 新增食材和步驟
- **輸出**：成功 → 重導向 `/recipes/<id>`；失敗 → 重新渲染 `recipes/new.html`
- **錯誤處理**：表單驗證失敗

### 2-5. `GET /recipes/<id>` — 食譜詳細頁

- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 呼叫 `recipe.get_recipe_by_id(id)` 取得食譜
  2. 呼叫 `recipe.get_ingredients_by_recipe(id)` 取得食材
  3. 呼叫 `recipe.get_steps_by_recipe(id)` 取得步驟
- **輸出**：渲染 `recipes/detail.html`
- **錯誤處理**：找不到 → 回傳 404

### 2-6. `GET /recipes/<id>/edit` / `POST /recipes/<id>/edit` — 編輯食譜

- **輸入**（POST）：同新增食譜
- **處理邏輯**：
  1. 驗證食譜存在且屬於目前使用者
  2. 呼叫 `recipe.update_recipe()` 更新主體
  3. 呼叫 `recipe.delete_ingredients_by_recipe()` 及 `recipe.delete_steps_by_recipe()` 清空
  4. 重新呼叫 `add_ingredient()` / `add_step()` 寫入
- **輸出**：成功 → 重導向 `/recipes/<id>`
- **錯誤處理**：404、權限不足 → 403

### 2-7. `POST /recipes/<id>/delete` — 刪除食譜

- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 驗證食譜存在且屬於目前使用者
  2. 呼叫 `recipe.delete_recipe(id)`（CASCADE 自動刪除食材與步驟）
- **輸出**：重導向 `/`
- **錯誤處理**：404、權限不足

### 2-8. `POST /recipes/scrape` — 萬用食譜抓取器

- **輸入**：表單欄位 `url`
- **處理邏輯**：
  1. 驗證 URL 格式
  2. 呼叫 `scraper.scrape_recipe(url)` 解析外部網頁
  3. 將解析結果暫存於 Flask `session`
- **輸出**：成功 → 渲染 `recipes/preview.html` 供使用者確認；失敗 → 返回並顯示錯誤訊息
- **錯誤處理**：URL 無效、解析失敗、逾時

### 2-9. `POST /recipes/scrape/confirm` — 確認儲存抓取結果

- **輸入**：從 `session` 讀取暫存的解析結果（使用者可在預覽頁微調）
- **處理邏輯**：
  1. 呼叫 `recipe.create_recipe()` + `add_ingredient()` + `add_step()` 完整寫入
  2. 清除 session 暫存資料
- **輸出**：重導向 `/recipes/<id>`

### 2-10. `POST /recipes/<id>/scale` — 智慧食材份量轉換

- **輸入**：表單欄位 `target_servings`
- **處理邏輯**：
  1. 呼叫 `recipe.get_recipe_by_id(id)` 取得原始份數
  2. 計算比例 `ratio = target_servings / original_servings`
  3. 取得食材並逐一乘以 ratio
- **輸出**：渲染 `recipes/detail.html`，傳入換算後的食材資料（不修改資料庫）
- **錯誤處理**：目標份數非正整數

### 2-11. `GET /recipes/<id>/cook` — 互動式下廚模式

- **輸入**：URL 參數 `id`
- **處理邏輯**：
  1. 取得食譜步驟列表
  2. 傳入步驟數量、計時資訊
- **輸出**：渲染 `recipes/cook.html`（含前端 JS 控制步驟切換與 Wake Lock）
- **錯誤處理**：404

### 2-12. `POST /shopping-list` — 產生採買清單

- **輸入**：表單欄位 `recipe_ids[]`, `servings[]`
- **處理邏輯**：
  1. 呼叫 `shopping.create_session()` 建立工作階段
  2. 迴圈呼叫 `shopping.add_recipe_to_session()` 關聯食譜
  3. 取得各食譜食材 → 依比例換算 → 合併同名食材 → 呼叫 `shopping.create_shopping_item()` 寫入
- **輸出**：重導向 `/shopping-list/<session_id>`

### 2-13. `POST /shopping-list/toggle/<item_id>` — 標記食材已購買

- **輸入**：URL 參數 `item_id`
- **處理邏輯**：呼叫 `shopping.toggle_purchased(item_id)`
- **輸出**：回傳 HTTP 200（前端 JS 做局部更新即可）

---

## 3. Jinja2 模板清單

| 模板路徑 | 繼承自 | 說明 |
|---------|--------|------|
| `templates/base.html` | — | 共用母版（Navbar、Footer、CSS/JS 引入） |
| `templates/index.html` | `base.html` | 首頁，食譜卡片列表、搜尋列 |
| `templates/register.html` | `base.html` | 註冊表單 |
| `templates/login.html` | `base.html` | 登入表單 |
| `templates/recipes/new.html` | `base.html` | 新增食譜表單（含動態食材/步驟欄位） |
| `templates/recipes/detail.html` | `base.html` | 食譜詳細頁（含份量換算區塊） |
| `templates/recipes/edit.html` | `base.html` | 編輯食譜表單 |
| `templates/recipes/preview.html` | `base.html` | 抓取結果預覽確認頁 |
| `templates/recipes/cook.html` | `base.html` | 互動式下廚模式（全螢幕步驟檢視） |
| `templates/shopping/list.html` | `base.html` | 採買清單頁面 |

---

## 4. 路由骨架程式碼

各路由骨架檔案位於 `app/routes/` 目錄：

| 檔案 | 說明 |
|------|------|
| `app/routes/__init__.py` | 路由套件初始化 |
| `app/routes/main_routes.py` | 首頁、註冊、登入、登出 |
| `app/routes/recipe_routes.py` | 食譜 CRUD、抓取器、採買清單 |
| `app/routes/cook_routes.py` | 下廚模式、份量換算 |

---

> 本文件由 `/api-design` skill 依據 `PRD.md`、`ARCHITECTURE.md` 與 `DB_DESIGN.md` 自動產出。  
> 最後更新：2026-04-28
