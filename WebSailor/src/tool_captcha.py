from qwen_agent.tools.base import BaseTool, register_tool
import json
import time
import requests


@register_tool("solve_captcha", allow_overwrite=True)
class CaptchaSolver(BaseTool):
    name = "solve_captcha"
    description = "2Captcha servisini kullanarak reCAPTCHA tokeni alir."

    parameters = {
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "description": "2Captcha API anahtari",
            },
            "site_key": {
                "type": "string",
                "description": "reCAPTCHA site key",
            },
            "url": {"type": "string", "description": "Captcha sayfa URL"},
        },
        "required": ["api_key", "site_key", "url"],
    }

    def call(self, params: dict, **kwargs) -> str:
        api_key = params.get("api_key")
        site_key = params.get("site_key")
        page_url = params.get("url")

        payload = {
            "key": api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
            "json": 1,
        }

        try:
            resp = requests.post("http://2captcha.com/in.php", data=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != 1:
                return json.dumps(data)
            request_id = data.get("request")
            result_params = {
                "key": api_key,
                "action": "get",
                "id": request_id,
                "json": 1,
            }
            for _ in range(20):
                time.sleep(5)
                result = requests.get(
                    "http://2captcha.com/res.php", params=result_params, timeout=10
                )
                result.raise_for_status()
                rj = result.json()
                if rj.get("status") == 1:
                    return rj.get("request")
            return "captcha çözülmedi"
        except Exception as e:
            return f"hata: {e}"

