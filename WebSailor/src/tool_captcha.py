"""Manual CAPTCHA handling utilities.

This module replaces the previous 2Captcha based implementation with a
user‑friendly manual approach.  When a CAPTCHA is detected the browser is
shown to the user and execution pauses until the user confirms that the
challenge is solved.  Optionally, a Streamlit UI can be used to provide
visual feedback and a confirmation button.
"""

from __future__ import annotations

import os
from typing import Optional


def detect_captcha(driver) -> bool:
    """Return ``True`` if the current page looks like a CAPTCHA."""

    page = driver.page_source.lower()
    return "captcha" in page or "robot" in page


def handle_captcha_ui(driver, page_url: Optional[str] = None) -> None:
    """Interactively resolve a CAPTCHA in the given ``driver``.

    The browser window is made visible and a screenshot is stored so that a UI
    framework such as Streamlit can display it.  Execution pauses until the
    user confirms that the CAPTCHA has been solved.
    """

    if not detect_captcha(driver):
        return

    if page_url:
        driver.get(page_url)

    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)

    screenshot_path = os.path.join(os.getcwd(), "captcha.png")
    driver.save_screenshot(screenshot_path)

    print("🔐 CAPTCHA detected!")
    print("📱 Browser açıldı - CAPTCHA'yı manuel çöz")
    print("✅ Çözdükten sonra bu pencereye dön ve Enter'a bas")

    try:
        import streamlit as st

        st.warning("CAPTCHA tespit edildi. Lütfen tarayıcıda çözün.")
        st.image(screenshot_path, caption="CAPTCHA ekran görüntüsü")
        st.button("CAPTCHA Çözüldü")
    except Exception:
        # Streamlit is optional; ignore if not available or not in a Streamlit
        # context.
        pass

    input("⏳ CAPTCHA çözüldü mü? (Enter'a bas): ")

    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

