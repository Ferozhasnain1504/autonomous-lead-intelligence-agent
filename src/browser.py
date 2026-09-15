import asyncio
import logging

from playwright.async_api import (
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)


logger = logging.getLogger(__name__)


class BrowserEngine:
    """Manages a Chromium browser for retrieving rendered web pages."""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30_000,
    ):
        self.headless = headless
        self.timeout = timeout
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        """Start Playwright and launch Chromium."""

        self._playwright = await async_playwright().start()

        self._browser = await self._playwright.chromium.launch(
            headless=self.headless
        )

    async def new_page(self) -> Page:
        """Create and configure a new browser page."""

        if self._browser is None:
            raise RuntimeError(
                "BrowserEngine has not been started."
            )

        page = await self._browser.new_page()

        page.set_default_timeout(self.timeout)

        return page

    async def fetch_page(
        self,
        page: Page,
        url: str,
    ) -> str | None:
        """
        Navigate to a URL and return the rendered HTML.

        Returns None when the page cannot be retrieved.
        """

        try:
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.timeout,
            )

            if response is None:
                logger.warning(
                    "No response received for %s",
                    url,
                )
                return None

            if response.status >= 400:
                logger.warning(
                    "HTTP %s while fetching %s",
                    response.status,
                    url,
                )
                return None

            return await page.content()

        except PlaywrightTimeoutError:
            logger.warning(
                "Timeout while fetching %s",
                url,
            )
            return None

        except Exception as error:
            logger.warning(
                "Failed to fetch %s: %s",
                url,
                error,
            )
            return None

    async def close(self) -> None:
        """Close the browser and Playwright."""

        if self._browser is not None:
            await self._browser.close()

        if self._playwright is not None:
            await self._playwright.stop()


async def main() -> None:
    """Simple manual test for the browser engine."""

    logging.basicConfig(level=logging.INFO)

    browser = BrowserEngine(headless=False)

    await browser.start()

    try:
        page = await browser.new_page()

        html = await browser.fetch_page(
            page,
            "https://example.com",
        )

        if html:
            print("Successfully fetched page.")
            print("HTML length:", len(html))
        else:
            print("Failed to fetch page.")

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())