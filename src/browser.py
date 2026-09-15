import asyncio

from playwright.async_api import Browser, Page, async_playwright


class BrowserEngine:
    """Manages a Chromium browser for retrieving rendered web pages."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Start Playwright and launch Chromium."""

        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless
        )

    async def new_page(self) -> Page:
        """Create and return a new browser page."""

        if self._browser is None:
            raise RuntimeError("BrowserEngine has not been started.")

        page = await self._browser.new_page()

        return page

    async def close(self) -> None:
        """Close the browser and Playwright."""

        if self._browser is not None:
            await self._browser.close()

        if self._playwright is not None:
            await self._playwright.stop()


async def main() -> None:
    """Simple manual test for the browser engine."""

    browser = BrowserEngine(headless=False)

    await browser.start()

    page = await browser.new_page()

    await page.goto(
        "https://supabase.com",
        wait_until="domcontentloaded",
        timeout=30_000,
    )

    print("URL:", page.url)
    print("Title:", await page.title())

    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())