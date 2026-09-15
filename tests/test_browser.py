import pytest

from src.browser import BrowserEngine


@pytest.mark.asyncio
async def test_browser_can_open_page():
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        page = await browser.new_page()

        html = await browser.fetch_page(
            page,
            "https://example.com",
        )

        assert html is not None
        assert "Example Domain" in html

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_fetch_page_returns_none_for_404():
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        page = await browser.new_page()

        html = await browser.fetch_page(
            page,
            "https://example.com/non-existent-page-12345",
        )

        assert html is None

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_fetch_page_returns_none_for_invalid_url():
    browser = BrowserEngine(headless=True)

    await browser.start()

    try:
        page = await browser.new_page()

        html = await browser.fetch_page(
            page,
            "https://this-domain-definitely-does-not-exist-12345.com",
        )

        assert html is None

    finally:
        await browser.close()