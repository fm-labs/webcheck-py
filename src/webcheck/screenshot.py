import base64

from playwright.async_api import async_playwright

from webcheck.conf import WEBCHECK_USER_AGENT

async def screenshot_handler(url: str):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_context = await browser.new_context(user_agent=WEBCHECK_USER_AGENT)
        page = await browser_context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
        except Exception:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        await page.set_viewport_size({"width": 1280, "height": 720})
        screenshot_data = await page.screenshot(path=None, full_page=True)
        await browser.close()

    base64_data = base64.b64encode(screenshot_data).decode("utf-8")
    return {
        "data": "data:image/png;base64," + base64_data
    }
