"""
app/utils/scraper.py
萬用食譜抓取器 — 從外部食譜網站解析食材與步驟
"""


def scrape_recipe(url: str) -> dict:
    """
    從指定 URL 抓取食譜內容。

    Args:
        url: 食譜網頁的完整 URL

    Returns:
        dict: 包含以下欄位的字典
            - title (str): 食譜名稱
            - description (str): 食譜簡介
            - servings (int): 份數
            - source_url (str): 原始來源
            - ingredients (list[dict]): 食材清單
            - steps (list[dict]): 步驟清單

    Raises:
        ValueError: URL 無效或解析失敗
    """
    # TODO: 實作網頁抓取與解析邏輯
    # 優先支援：愛料理 (icook.tw)
    pass
