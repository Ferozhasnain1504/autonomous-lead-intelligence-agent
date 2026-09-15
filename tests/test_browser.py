import pytest

from src.browser import BrowserEngine


@pytest.mark.asyncio
async def test_browser_can_open_page():
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        page = await browser.new_page()

        await page.goto(
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        assert await page.title() == "Example Domain"

    finally:
        await browser.close()