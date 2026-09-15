from bs4 import BeautifulSoup


class ContentCleaner:
    """Converts raw HTML into clean text suitable for LLM processing."""

    ELEMENTS_TO_REMOVE = [
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "nav",
        "footer",
    ]

    def clean(self, html: str) -> str:
        """
        Convert raw HTML into clean, readable text.

        Args:
            html: Raw HTML content.

        Returns:
            Cleaned page text.
        """

        if not html:
            return ""

        soup = BeautifulSoup(html, "lxml")

        self._remove_irrelevant_elements(soup)

        text_blocks = []

        for element in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
        ):
            text = " ".join(" ".join(element.stripped_strings).split())

            if text:
                text_blocks.append(text)

        return "\n".join(text_blocks)

    def _remove_irrelevant_elements(self, soup: BeautifulSoup) -> None:
        """Remove elements that do not contribute useful page content."""

        for element_name in self.ELEMENTS_TO_REMOVE:
            for element in soup.find_all(element_name):
                element.decompose()