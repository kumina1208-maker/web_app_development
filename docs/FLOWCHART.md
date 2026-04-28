# 食譜收藏系統 - 流程圖設計文件

本文件依據 `PRD.md` 與 `ARCHITECTURE.md` 產出，包含三個部分：
1. **使用者流程圖（User Flow）**：描述使用者的操作路徑
2. **系統序列圖（System Sequence Diagram）**：描述資料在系統內的流動
3. **功能清單對照表**：功能、URL 與 HTTP 方法一覽

---

## 1. 使用者流程圖（User Flow）

以下流程圖涵蓋本系統所有 MVP 核心功能的使用者操作路徑，包含：食譜管理（新增/瀏覽/編輯/刪除）、自動化採買清單、智慧份量轉換、互動式下廚模式，以及萬用食譜抓取器。

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁 - 食譜列表]

    B --> C{選擇操作}

    %% 新增食譜
    C -->|手動新增食譜| D[點擊「新增食譜」按鈕]
    D --> E[填寫食譜表單\n食譜名稱、食材清單、步驟、份數、標籤]
    E --> F{表單驗證}
    F -->|驗證失敗| E
    F -->|驗證成功| G[儲存食譜到資料庫]
    G --> B

    %% 抓取食譜
    C -->|URL 抓取食譜| H[貼上食譜網址]
    H --> I[系統解析外部網頁]
    I --> J{解析是否成功？}
    J -->|失敗| K[顯示錯誤訊息]
    K --> H
    J -->|成功| L[預覽解析出的食材與步驟]
    L --> M{確認儲存？}
    M -->|取消| B
    M -->|確認| G

    %% 瀏覽食譜
    C -->|點擊食譜| N[食譜詳細頁面]
    N --> O{選擇操作}

    %% 編輯
    O -->|編輯| P[填寫編輯表單]
    P --> Q{表單驗證}
    Q -->|驗證失敗| P
    Q -->|成功| R[更新資料庫]
    R --> N

    %% 刪除
    O -->|刪除| S[確認刪除對話框]
    S -->|取消| N
    S -->|確認刪除| T[從資料庫刪除]
    T --> B

    %% 份量轉換
    O -->|份量轉換| U[輸入目標份數]
    U --> V[系統自動重算所有食材用量]
    V --> N

    %% 下廚模式
    O -->|開啟下廚模式| W[進入互動式下廚介面\n步驟放大顯示 / 螢幕常亮]
    W --> X{切換步驟}
    X -->|點擊 / 語音| X
    X -->|完成烹飪| N

    %% 採買清單
    C -->|採買清單| Y[勾選多張食譜]
    Y --> Z[系統彙整所有食材與用量]
    Z --> AA[顯示採買清單]
    AA --> AB{清單操作}
    AB -->|標記已購買| AA
    AB -->|返回| B
```

---

## 2. 系統序列圖（System Sequence Diagram）

以下序列圖以五個核心功能為主軸，分別描述使用者操作觸發後的完整系統資料流。

### 2-1. 手動新增食譜

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Routes
    participant Model as Recipe Model
    participant DB as SQLite

    User->>Browser: 點擊「新增食譜」按鈕
    Browser->>Flask: GET /recipes/new
    Flask-->>Browser: 渲染空白食譜表單 (new.html)

    User->>Browser: 填寫食譜資料並送出
    Browser->>Flask: POST /recipes/new
    Flask->>Flask: 表單驗證與資料清洗
    Flask->>Model: create_recipe(data)
    Model->>DB: INSERT INTO recipes ...
    DB-->>Model: 回傳新 recipe_id
    Model-->>Flask: 回傳成功
    Flask-->>Browser: 302 重導向到 /recipes/<id>
    Browser->>Flask: GET /recipes/<id>
    Flask->>Model: get_recipe(id)
    Model->>DB: SELECT * FROM recipes WHERE id=?
    DB-->>Model: 回傳食譜資料
    Model-->>Flask: 食譜物件
    Flask-->>Browser: 渲染食譜詳細頁 (recipe.html)
```

### 2-2. 萬用食譜抓取器

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Routes
    participant Scraper as Scraper Utils
    participant External as 外部食譜網站
    participant Model as Recipe Model
    participant DB as SQLite

    User->>Browser: 貼上食譜網址並送出
    Browser->>Flask: POST /recipes/scrape
    Flask->>Scraper: scrape_recipe(url)
    Scraper->>External: HTTP GET 請求目標網頁
    External-->>Scraper: 回傳 HTML 內容
    Scraper->>Scraper: BeautifulSoup 解析食材與步驟
    Scraper-->>Flask: 回傳解析結果 (dict)

    alt 解析失敗
        Flask-->>Browser: 顯示錯誤訊息頁
    else 解析成功
        Flask-->>Browser: 渲染預覽頁面 (preview.html)
        User->>Browser: 確認儲存
        Browser->>Flask: POST /recipes/scrape/confirm
        Flask->>Model: create_recipe(parsed_data)
        Model->>DB: INSERT INTO recipes ...
        DB-->>Model: 回傳 recipe_id
        Flask-->>Browser: 302 重導向到 /recipes/<id>
    end
```

### 2-3. 智慧食材份量轉換

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Routes
    participant Model as Recipe Model
    participant DB as SQLite

    User->>Browser: 在食譜詳細頁輸入目標份數並送出
    Browser->>Flask: POST /recipes/<id>/scale
    Flask->>Model: get_recipe(id)
    Model->>DB: SELECT * FROM recipes WHERE id=?
    DB-->>Model: 回傳原始食譜資料（含原始份數）
    Model-->>Flask: 食譜物件
    Flask->>Flask: 計算比例 (target / original)\n依比例乘算所有食材用量
    Flask-->>Browser: 渲染含換算後食材的食譜頁 (recipe.html)
```

### 2-4. 自動化採買清單

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Routes
    participant Model as ShoppingList Model
    participant DB as SQLite

    User->>Browser: 在食譜列表勾選多張食譜並送出
    Browser->>Flask: POST /shopping-list
    Note right of Browser: 送出勾選的 recipe_id 清單

    loop 每張食譜
        Flask->>Model: get_ingredients(recipe_id)
        Model->>DB: SELECT ingredients WHERE recipe_id=?
        DB-->>Model: 回傳食材清單
        Model-->>Flask: 食材資料
    end

    Flask->>Flask: 彙整所有食材\n合併相同食材並加總用量
    Flask-->>Browser: 渲染採買清單頁 (shopping_list.html)

    User->>Browser: 點擊食材標記為「已購買」
    Browser->>Flask: POST /shopping-list/toggle/<item_id>
    Flask->>Model: toggle_purchased(item_id)
    Model->>DB: UPDATE shopping_items SET purchased=?
    DB-->>Model: 成功
    Flask-->>Browser: 200 OK (或局部更新)
```

### 2-5. 互動式下廚模式

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Routes
    participant Model as Recipe Model
    participant DB as SQLite
    participant WakeLock as Screen Wake Lock API

    User->>Browser: 點擊「開始下廚」按鈕
    Browser->>Flask: GET /recipes/<id>/cook
    Flask->>Model: get_recipe(id)
    Model->>DB: SELECT steps FROM recipes WHERE id=?
    DB-->>Model: 回傳步驟資料
    Model-->>Flask: 食譜步驟列表
    Flask-->>Browser: 渲染下廚模式頁 (cook.html)

    Browser->>WakeLock: navigator.wakeLock.request('screen')
    WakeLock-->>Browser: 螢幕常亮鎖定成功

    loop 烹飪中
        User->>Browser: 點擊「下一步」或語音指令
        Browser->>Browser: JS 切換至下一個步驟\n更新進度指示器
    end

    User->>Browser: 點擊「完成烹飪」
    Browser->>WakeLock: 釋放 Wake Lock
    Browser->>Flask: GET /recipes/<id>
    Flask-->>Browser: 返回食譜詳細頁
```

---

## 3. 功能清單對照表

| # | 功能名稱 | URL 路徑 | HTTP 方法 | Controller 路由檔案 | 說明 |
|---|---------|---------|----------|-------------------|------|
| 1 | 首頁 / 食譜列表 | `/` | GET | `main_routes.py` | 顯示所有食譜，支援搜尋與篩選 |
| 2 | 新增食譜頁面 | `/recipes/new` | GET | `recipe_routes.py` | 渲染空白新增表單 |
| 3 | 送出新增食譜 | `/recipes/new` | POST | `recipe_routes.py` | 接收表單資料，寫入資料庫 |
| 4 | 食譜詳細頁面 | `/recipes/<id>` | GET | `recipe_routes.py` | 顯示食譜完整內容 |
| 5 | 編輯食譜頁面 | `/recipes/<id>/edit` | GET | `recipe_routes.py` | 渲染預填資料的編輯表單 |
| 6 | 送出編輯食譜 | `/recipes/<id>/edit` | POST | `recipe_routes.py` | 更新資料庫中的食譜資料 |
| 7 | 刪除食譜 | `/recipes/<id>/delete` | POST | `recipe_routes.py` | 從資料庫刪除指定食譜 |
| 8 | URL 抓取食譜 | `/recipes/scrape` | POST | `recipe_routes.py` | 傳入網址，呼叫 scraper 解析並預覽 |
| 9 | 確認儲存抓取食譜 | `/recipes/scrape/confirm` | POST | `recipe_routes.py` | 確認後將解析結果寫入資料庫 |
| 10 | 份量換算 | `/recipes/<id>/scale` | POST | `cook_routes.py` | 接收目標份數，回傳換算後食材頁面 |
| 11 | 下廚模式 | `/recipes/<id>/cook` | GET | `cook_routes.py` | 進入互動式下廚模式介面 |
| 12 | 採買清單產生 | `/shopping-list` | POST | `recipe_routes.py` | 接收多張食譜 ID，彙整並顯示採買清單 |
| 13 | 標記食材已購買 | `/shopping-list/toggle/<item_id>` | POST | `recipe_routes.py` | 切換食材的已購買狀態 |

---

> 本文件由 `/flowchart` skill 依據 `PRD.md` 與 `ARCHITECTURE.md` 自動產出。
> 最後更新：2026-04-28
