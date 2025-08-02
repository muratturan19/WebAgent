from qwen_agent.tools.base import BaseTool, register_tool
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import time


@register_tool("login", allow_overwrite=True)
class SahibindenAuth(BaseTool):
    name = "login"
    description = "Sahibinden.com'a kullanıcı girişi yapar ve oturum çerezlerini döner."

    parameters = {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Kullanıcı adı veya e-posta",
            },
            "password": {"type": "string", "description": "Şifre"},
        },
        "required": ["username", "password"],
    }

    def call(self, params: dict, **kwargs) -> str:
        username = params.get("username")
        password = params.get("password")
        options = uc.ChromeOptions()
        options.headless = True
        driver = uc.Chrome(options=options)
        try:
            driver.get("https://www.sahibinden.com/giris")
            time.sleep(2)
            driver.find_element(By.ID, "username").send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "password").submit()
            time.sleep(3)
            cookies = driver.get_cookies()
            return json.dumps(cookies, ensure_ascii=False)
        except Exception as e:
            return f"giris basarisiz: {e}"
        finally:
            driver.quit()

