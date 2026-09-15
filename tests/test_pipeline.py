import pytest

from src.pipeline import EnrichmentPipeline
from src.schemas import CompanyIntelligence, LeadershipPerson


class FakePage:

    async def close(self):
        pass


class FakeBrowser:

    def __init__(self):
        self.requested_urls = []

    async def new_page(self):
        return FakePage()

    async def fetch_page(self, page, url):
        self.requested_urls.append(url)

        return """
        <html>
            <main>
                <h1>Example Corp</h1>
                <p>
                    Example Corp builds software for developers.
                </p>
            </main>
        </html>
        """


class FakePageDiscovery:

    async def discover(self, page):
        return []


class FakeCleaner:

    def clean(self, html):
        return "Example Corp builds software for developers."


class FakeExtractor:

    async def extract(self, text):
        return CompanyIntelligence(
            company_name="Example Corp",
            company_overview=(
                "Example Corp builds software for developers. "
                "Its platform helps development teams."
            ),
            target_audience="Software developers",
            public_emails=[],
            leadership=[],
            confidence_score=0.9,
        )


class FakeExternalSearch:

    async def find_linkedin_profile(
        self,
        person_name,
        company_name,
    ):
        return "https://www.linkedin.com/in/janedoe"


class FakeExtractorWithLeader:

    async def extract(self, text):
        return CompanyIntelligence(
            company_name="Example Corp",
            company_overview=(
                "Example Corp builds software for developers. "
                "Its platform helps development teams."
            ),
            target_audience="Software developers",
            public_emails=[],
            leadership=[
                LeadershipPerson(
                    name="Jane Doe",
                    role="CEO",
                )
            ],
            confidence_score=0.9,
        )


class FakeExtractorWithExistingLinkedIn:

    async def extract(self, text):
        return CompanyIntelligence(
            company_name="Example Corp",
            company_overview=(
                "Example Corp builds software for developers. "
                "Its platform helps development teams."
            ),
            target_audience="Software developers",
            public_emails=[],
            leadership=[
                LeadershipPerson(
                    name="Jane Doe",
                    role="CEO",
                    linkedin_url=(
                        "https://www.linkedin.com/in/existing"
                    ),
                )
            ],
            confidence_score=0.9,
        )


class FakeExternalSearchShouldNotRun:

    async def find_linkedin_profile(
        self,
        person_name,
        company_name,
    ):
        raise AssertionError(
            "External search should not run when LinkedIn URL exists."
        )


@pytest.mark.asyncio
async def test_enrich_company():

    browser = FakeBrowser()

    pipeline = EnrichmentPipeline(
        browser=browser,
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractor(),
    )

    result = await pipeline.enrich_company(
        "example.com"
    )

    assert result is not None
    assert result.company_name == "Example Corp"
    assert result.target_audience == "Software developers"
    assert result.confidence_score == 0.9

    assert browser.requested_urls == [
        "https://example.com"
    ]


@pytest.mark.asyncio
async def test_multiple_companies_continue_after_failure():

    class FailingBrowser(FakeBrowser):

        async def fetch_page(self, page, url):
            self.requested_urls.append(url)

            if "bad-domain" in url:
                raise RuntimeError("Simulated failure")

            return """
            <html>
                <main>
                    <h1>Example Corp</h1>
                    <p>Software company.</p>
                </main>
            </html>
            """

    browser = FailingBrowser()

    pipeline = EnrichmentPipeline(
        browser=browser,
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractor(),
    )

    results = await pipeline.enrich_companies(
        [
            "example.com",
            "bad-domain.com",
            "another-example.com",
        ]
    )

    assert results["example.com"] is not None
    assert results["bad-domain.com"] is None
    assert results["another-example.com"] is not None


def test_normalize_domain_adds_https():

    pipeline = EnrichmentPipeline(
        browser=FakeBrowser(),
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractor(),
    )

    assert pipeline._normalize_domain(
        "example.com"
    ) == "https://example.com"


def test_normalize_domain_removes_trailing_slash():

    pipeline = EnrichmentPipeline(
        browser=FakeBrowser(),
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractor(),
    )

    assert pipeline._normalize_domain(
        "https://example.com/"
    ) == "https://example.com"


def test_normalize_domain_rejects_empty_value():

    pipeline = EnrichmentPipeline(
        browser=FakeBrowser(),
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractor(),
    )

    with pytest.raises(ValueError):
        pipeline._normalize_domain("")


@pytest.mark.asyncio
async def test_pipeline_adds_missing_linkedin_profile():

    browser = FakeBrowser()

    pipeline = EnrichmentPipeline(
        browser=browser,
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractorWithLeader(),
        external_search=FakeExternalSearch(),
    )

    result = await pipeline.enrich_company(
        "example.com"
    )

    assert result is not None
    assert len(result.leadership) == 1
    assert result.leadership[0].name == "Jane Doe"
    assert str(result.leadership[0].linkedin_url) == (
    "https://www.linkedin.com/in/janedoe"
    )


@pytest.mark.asyncio
async def test_pipeline_keeps_existing_linkedin_profile():

    browser = FakeBrowser()

    pipeline = EnrichmentPipeline(
        browser=browser,
        page_discovery=FakePageDiscovery(),
        content_cleaner=FakeCleaner(),
        extractor=FakeExtractorWithExistingLinkedIn(),
        external_search=FakeExternalSearchShouldNotRun(),
    )

    result = await pipeline.enrich_company(
        "example.com"
    )

    assert result is not None
    assert len(result.leadership) == 1
    assert str(result.leadership[0].linkedin_url) == (
        "https://www.linkedin.com/in/existing"
    )