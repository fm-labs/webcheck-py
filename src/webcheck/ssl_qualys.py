import base64
import time

from playwright.async_api import async_playwright

from webcheck.conf import WEBCHECK_USER_AGENT

async def qualys_sslchecker_handler(domain: str):

    url = f"https://www.ssllabs.com/ssltest/analyze.html?d={domain}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_context = await browser.new_context(user_agent=WEBCHECK_USER_AGENT)

        should_continue = True
        while (should_continue):
            page = await browser_context.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=15000)
            except TimeoutError:
                pass  # Continue even if timeout occurs

            # Fetch the html body
            html = await page.content()
            # Find the string "Please wait..." to check if the analysis is still in progress
            if "Please wait..." in html or "Analysis in progress" in html:
                print("SSL Labs analysis still in progress, waiting...")
                should_continue = True
                await page.close()
                time.sleep(5)
            else:
                should_continue = False

        print("SSL Labs analysis completed.")
        await page.set_viewport_size({"width": 1280, "height": 720})
        screenshot_data = await page.screenshot(path=None, full_page=True)
        await browser.close()

    base64_data = base64.b64encode(screenshot_data).decode("utf-8")
    return {
        "html": html,
        "screenshot": "data:image/png;base64," + base64_data
    }
