from qwen_agent.tools.base import BaseTool, register_tool
from typing import List, Union
import requests
from bs4 import BeautifulSoup
import json


@register_tool("visit", allow_overwrite=True)
class Visit(BaseTool):
    name = "visit"
    description = (
        "Sahibinden.com ilan sayfalarını ziyaret eder ve başlık, fiyat, açıklama gibi bilgileri döner."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": ["string", "array"],
                "items": {"type": "string"},
                "description": "Ziyaret edilecek ilan URL'si veya URL listesi",
            },
            "goal": {
                "type": "string",
                "description": "(İsteğe bağlı) Sayfadan istenen ek bilgi",
            },
        },
        "required": ["url"],
    }

    def _fetch(self, url: str):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            )
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            return {"url": url, "hata": str(e)}

        soup = BeautifulSoup(resp.text, "html.parser")
        data = {"url": url}
        title = soup.select_one("#classifiedTitle")
        price = soup.select_one("div.classifiedInfo h3")
        desc = soup.select_one("div.classifiedDescription")
        if title:
            data["baslik"] = title.get_text(strip=True)
        if price:
            data["fiyat"] = price.get_text(" ", strip=True)
        if desc:
            data["aciklama"] = desc.get_text(" ", strip=True)
        return data

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            url = params["url"]
        except Exception:
            return "[visit] 'url' alanı eksik"

        urls = url if isinstance(url, list) else [url]
        results = [self._fetch(u) for u in urls]
        return json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False)

