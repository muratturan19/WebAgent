from qwen_agent.tools.base import BaseTool, register_tool
import json
from typing import List, Union
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup


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

    def _search_once(self, query: str):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }
        url = f"https://www.sahibinden.com/arama?query_text={quote_plus(query)}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            return {"sorgu": query, "hata": str(e)}

        soup = BeautifulSoup(resp.text, "html.parser")
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
        return {"sorgu": query, "sonuclar": items}

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            query = params["query"]
        except Exception:
            return "[search] 'query' alanı eksik"

        queries = query if isinstance(query, list) else [query]
        results = [self._search_once(q) for q in queries]
        return json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False)

