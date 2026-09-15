import logging

from src.browser import BrowserEngine
from src.content_cleaner import ContentCleaner
from src.gemini_extractor import GeminiExtractor
from src.page_discovery import PageDiscovery
from src.safe_runner import run_safely
from src.schemas import CompanyIntelligence


logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    """Coordinates the complete company enrichment workflow."""

    def __init__(
        self,
        browser: BrowserEngine,
        page_discovery: PageDiscovery | None = None,
        content_cleaner: ContentCleaner | None = None,
        extractor: GeminiExtractor | None = None,
    ):
        self.browser = browser
        self.page_discovery = (
            page_discovery or PageDiscovery()
        )
        self.content_cleaner = (
            content_cleaner or ContentCleaner()
        )
        self.extractor = extractor or GeminiExtractor()

    async def enrich_company(
        self,
        domain: str,
    ) -> CompanyIntelligence | None:
        """
        Enrich a single company domain.

        Returns None if the company cannot be processed.
        """

        url = self._normalize_domain(domain)

        logger.info("Starting enrichment for %s", url)

        page = await self.browser.new_page()

        try:
            homepage_html = await self.browser.fetch_page(
                page,
                url,
            )

            if homepage_html is None:
                logger.warning(
                    "Could not retrieve homepage for %s",
                    domain,
                )
                return None

            homepage_text = self.content_cleaner.clean(
                homepage_html
            )

            relevant_urls = await self.page_discovery.discover(
                page
            )

            all_text = [homepage_text]

            for relevant_url in relevant_urls:
                html = await self.browser.fetch_page(
                    page,
                    relevant_url,
                )

                if html is None:
                    logger.warning(
                        "Skipping failed page: %s",
                        relevant_url,
                    )
                    continue

                cleaned_text = self.content_cleaner.clean(
                    html
                )

                if cleaned_text:
                    all_text.append(cleaned_text)

            combined_text = "\n\n".join(all_text)

            result = await self.extractor.extract(
                combined_text
            )

            logger.info(
                "Successfully enriched %s",
                domain,
            )

            return result

        except Exception as error:
            logger.warning(
                "Company enrichment failed for %s: %s",
                domain,
                error,
            )
            return None

        finally:
            await page.close()

    async def enrich_companies(
        self,
        domains: list[str],
    ) -> dict[str, CompanyIntelligence | None]:
        """
        Enrich multiple companies.

        A failure for one company does not stop the others.
        """

        results = {}

        for domain in domains:
            result = await run_safely(
                lambda domain=domain: self.enrich_company(
                    domain
                ),
                f"enrichment for {domain}",
            )

            results[domain] = result

        return results

    def _normalize_domain(self, domain: str) -> str:
        """Convert a domain into a usable HTTPS URL."""

        domain = domain.strip()

        if not domain:
            raise ValueError("Domain cannot be empty.")

        if not domain.startswith(
            ("http://", "https://")
        ):
            domain = f"https://{domain}"

        return domain.rstrip("/")