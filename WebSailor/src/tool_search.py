from qwen_agent.tools.base import BaseTool, register_tool
import json
from typing import List, Union
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc



@register_tool("search", allow_overwrite=True)
class Search(BaseTool):
    name = "search"
    description = (
        "Sahibinden.com'da arama yapar ve sonuçları başlık, fiyat ve link olarak döner."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": ["string", "array"],
                "items": {"type": "string"},
                "description": "Arama yapılacak kelime veya kelimeler.",
            }
        },
        "required": ["query"],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
        )

    def _search_once(self, query: str):
        url = f"https://www.sahibinden.com/arama?query_text={quote_plus(query)}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            items = self._parse_soup(soup)
            if not items:
                items = self._selenium_fetch(url)
            return {"sorgu": query, "sonuclar": items}
        except Exception:
            try:
                items = self._selenium_fetch(url)
                return {"sorgu": query, "sonuclar": items}
            except Exception as e2:
                return {"error": str(e2)}
        finally:
            time.sleep(3)

    def _parse_soup(self, soup: BeautifulSoup):
        items = []
        for row in soup.select("tr.searchResultsItem")[:10]:
            title_elem = row.select_one("td.searchResultsTitleValue a")
            price_elem = row.select_one("td.searchResultsPriceValue")
            if not title_elem or not price_elem:
                continue
            title = title_elem.get_text(strip=True)
            price = price_elem.get_text(" ", strip=True)
            link = "https://www.sahibinden.com" + title_elem.get("href", "")
            items.append({"baslik": title, "fiyat": price, "link": link})
        return items

    def _selenium_fetch(self, url: str):
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)
        try:
            driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return self._parse_soup(soup)
        finally:
            driver.quit()

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            query = params["query"]
        except Exception:
            return "[search] 'query' alanı eksik"

        queries = query if isinstance(query, list) else [query]
        results = [self._search_once(q) for q in queries]
        return json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False)

