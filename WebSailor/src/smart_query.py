from qwen_agent.tools.base import BaseTool, register_tool
import json
import requests


@register_tool("smart_query", allow_overwrite=True)
class SmartQuery(BaseTool):
    name = "smart_query"
    description = "Verilen anahtar kelimeler için öneri sorgular üretir."

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
            resp = requests.get(
                "https://api.datamuse.com/words",
                params={"ml": query, "max": 5},
                timeout=10,
            )
            resp.raise_for_status()
            suggestions = [item.get("word") for item in resp.json()]
            return json.dumps(
                {"query": query, "suggestions": suggestions}, ensure_ascii=False
            )
        except Exception as e:
            return f"hata: {e}"

