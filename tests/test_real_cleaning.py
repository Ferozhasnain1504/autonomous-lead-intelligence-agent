import pytest

from src.browser import BrowserEngine
from src.content_cleaner import ContentCleaner


@pytest.mark.asyncio
async def test_clean_postman_content():
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        page = await browser.new_page()

        await page.goto(
            "https://www.postman.com/company/about-postman/",
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        html = await page.content()

        cleaner = ContentCleaner()

        clean_text = cleaner.clean(html)

        print("\n" + "=" * 60)
        print("CLEANED POSTMAN CONTENT")
        print("=" * 60)
        print(clean_text[:5000])
        print("=" * 60)

        assert len(clean_text) > 100

    finally:
        await browser.close()