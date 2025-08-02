from qwen_agent.tools.base import BaseTool, register_tool
import json
import re


@register_tool("smart_query", allow_overwrite=True)
class SmartQuery(BaseTool):
    name = "smart_query"
    description = "Türkçe sorguları analiz ederek yapılandırılmış bilgi çıkarır."

    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Arama sorgusu"}
        },
        "required": ["query"],
    }

    def call(self, params: dict, **kwargs) -> str:
        query = params.get("query", "")
        try:
            parsed = self._parse_query(query)
            return json.dumps({"query": query, "parsed": parsed}, ensure_ascii=False)
        except Exception as e:
            return f"hata: {e}"

    def _parse_query(self, query: str) -> dict:
        ql = query.lower()

        oda_match = re.search(r"\b\d+\+\d+\b", ql)
        oda = oda_match.group(0) if oda_match else None

        tip = None
        if "kiralık" in ql:
            tip = "kiralık"
        elif "satılık" in ql:
            tip = "satılık"

        kategori = "emlak" if any(k in ql for k in ["daire", "ev", "emlak", "konut"]) else None

        loc = None
        loc_match = re.search(r"([\wÇĞİÖŞÜçğıöşü]+)['’]?(?:de|da|te|ta)\b", query)
        if loc_match:
            loc = loc_match.group(1)

        return {
            "konum": loc,
            "oda_sayisi": oda,
            "tip": tip,
            "kategori": kategori,
        }

