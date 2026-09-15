from urllib.parse import urljoin, urlparse

from playwright.async_api import Page


class PageDiscovery:
    """Discovers relevant internal pages from a company's homepage."""

    RELEVANT_KEYWORDS = {
        "about": 10,
        "team": 10,
        "company": 9,
        "contact": 9,
        "pricing": 8,
        "leadership": 8,
        "people": 7,
        "product": 6,
        "solutions": 6,
        "customers": 5,
        "careers": 5,
    }

    def __init__(self, max_pages: int = 5):
        self.max_pages = max_pages

    async def discover(self, page: Page) -> list[str]:
        """Discover the most relevant internal pages."""

        homepage_url = page.url

        links = await page.locator("a").evaluate_all(
            """
            anchors => anchors.map(anchor => ({
                href: anchor.href,
                text: anchor.innerText
            }))
            """
        )

        candidates = []

        for link in links:
            href = link.get("href", "")
            text = link.get("text", "")

            if not href:
                continue

            absolute_url = urljoin(homepage_url, href)

            if not self._is_internal_link(homepage_url, absolute_url):
                continue

            score = self._calculate_relevance_score(
                url=absolute_url,
                text=text,
            )

            if score <= 0:
                continue

            candidates.append(
                {
                    "url": absolute_url,
                    "score": score,
                }
            )

        candidates.sort(
            key=lambda candidate: candidate["score"],
            reverse=True,
        )

        return self._remove_duplicates(
            candidates[: self.max_pages]
        )

    def _calculate_relevance_score(
        self,
        url: str,
        text: str,
    ) -> int:
        """Calculate how relevant a link is."""

        parsed_url = urlparse(url)

        path = parsed_url.path.lower()
        link_text = text.lower()

        score = 0

        for keyword, keyword_score in self.RELEVANT_KEYWORDS.items():
            if keyword in path:
                score += keyword_score

            if keyword in link_text:
                score += keyword_score

        return score

    def _is_internal_link(
        self,
        homepage_url: str,
        target_url: str,
    ) -> bool:
        """Check whether a URL belongs to the same domain."""

        homepage_domain = urlparse(homepage_url).netloc
        target_domain = urlparse(target_url).netloc

        return homepage_domain == target_domain

    def _remove_duplicates(
        self,
        candidates: list[dict],
    ) -> list[str]:
        """Remove duplicate URLs while preserving ranking order."""

        seen = set()
        results = []

        for candidate in candidates:
            url = candidate["url"]

            if url in seen:
                continue

            seen.add(url)
            results.append(url)

        return results