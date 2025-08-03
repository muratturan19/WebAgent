from qwen_agent.tools.base import BaseTool, register_tool
import json
import os
from typing import Union
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from dotenv import load_dotenv, find_dotenv

from tool_auth import SahibindenAuth
from tool_captcha import handle_captcha_ui, detect_captcha

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session_cookies.json")



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
        load_dotenv(find_dotenv())
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
        self._load_cookies()

    def _load_cookies(self, refresh: bool = False) -> None:
        cookies = None
        if not refresh and os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            except Exception:
                cookies = None
        if cookies is None:
            auth = SahibindenAuth()
            cookie_str = auth.call({})
            try:
                cookies = json.loads(cookie_str)
            except Exception:
                cookies = []
        for c in cookies:
            self.session.cookies.set(c.get("name"), c.get("value"))

    def _search_once(self, query: str):
        url = f"https://www.sahibinden.com/arama?query_text={quote_plus(query)}"
        try:
            resp = self.session.get(url, timeout=10)
            if "giris" in resp.url:
                self._load_cookies(refresh=True)
                resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            items = self._parse_soup(soup)
            if not items:
                items = self._selenium_fetch(url)
            return {"sorgu": query, "sonuclar": items}
        except Exception as e:
            try:
                items = self._selenium_fetch(url)
                return {"sorgu": query, "sonuclar": items}
            except Exception as e2:
                return {"error": f"arama basarisiz: {e2}"}
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
            driver.get("https://www.sahibinden.com")
            for c in self.session.cookies:
                driver.add_cookie({"name": c.name, "value": c.value})
            driver.get(url)
            if detect_captcha(driver):
                driver.quit()
                options.headless = False
                driver = uc.Chrome(options=options)
                driver.get(url)
                handle_captcha_ui(driver, url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return self._parse_soup(soup)
        finally:
            driver.quit()

    async def navigate_to_category(self, page, category_path):
        try:
            await page.goto("https://www.sahibinden.com")
            await page.wait_for_load_state('networkidle')

            category_map = {
                'emlak': 'a:has-text("Emlak")',
                'konut': 'a:has-text("Konut")',
                'is_yeri': 'a:has-text("İş Yeri")',
                'arsa': 'a:has-text("Arsa")',
                'vasita': 'a:has-text("Vasıta")',
                'otomobil': 'a:has-text("Otomobil")'
            }

            for category in category_path:
                if category.lower() in category_map:
                    selector = category_map[category.lower()]
                    await page.click(selector)
                    await page.wait_for_load_state('networkidle')

            return True, "Navigation successful"

        except Exception as e:
            return False, f"Navigation failed: {e}"

    async def search_with_filters(self, page, parsed):
        query = " ".join(parsed.get('keywords', [])) if isinstance(parsed.get('keywords'), list) else parsed.get('keywords', '')
        return self._search_once(query)

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            query = params["query"]
        except Exception:
            return "[search] 'query' alanı eksik"

        queries = query if isinstance(query, list) else [query]
        results = [self._search_once(q) for q in queries]
        return json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False)

