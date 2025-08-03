from qwen_agent.tools.base import BaseTool, register_tool
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import os
import time
from dotenv import load_dotenv, find_dotenv

from tool_captcha import handle_captcha_ui, detect_captcha

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session_cookies.json")


@register_tool("login", allow_overwrite=True)
class SahibindenAuth(BaseTool):
    name = "login"
    description = "Sahibinden.com'a kullanıcı girişi yapar ve oturum çerezlerini döner."

    # Credentials are read from environment variables.  No parameters are
    # required for this tool.
    parameters = {"type": "object", "properties": {}, "required": []}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_dotenv(find_dotenv())
        self.username = os.getenv("SAHIBINDEN_EMAIL")
        self.password = os.getenv("SAHIBINDEN_PASSWORD")

    def call(self, params: dict, **kwargs) -> str:
        username = self.username
        password = self.password

        if not username or not password:
            return "giris basarisiz: kredensiyeller bulunamadi"

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

            if detect_captcha(driver):
                driver.quit()
                options.headless = False
                driver = uc.Chrome(options=options)
                driver.get("https://www.sahibinden.com/giris")
                time.sleep(2)
                driver.find_element(By.ID, "username").send_keys(username)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.ID, "password").submit()
                handle_captcha_ui(driver, driver.current_url)
                time.sleep(3)

            cookies = driver.get_cookies()
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False)
            return json.dumps(cookies, ensure_ascii=False)
        except Exception as e:
            return f"giris basarisiz: {e}"
        finally:
            driver.quit()

