from src.external_search import ExternalSearch


class FakeSearchClient:
    """Fake Tavily client for testing."""

    def search(self, **kwargs):
        return {
            "results": [
                {
                    "title": "Jane Doe - LinkedIn",
                    "url": "https://www.linkedin.com/in/janedoe",
                }
            ]
        }


class FakeSearchClientWithoutLinkedIn:
    """Fake search client with no LinkedIn profile."""

    def search(self, **kwargs):
        return {
            "results": [
                {
                    "title": "Jane Doe - Company Profile",
                    "url": "https://example.com/team/jane",
                }
            ]
        }


def test_finds_linkedin_profile():
    search = ExternalSearch(client=FakeSearchClient())

    import asyncio

    result = asyncio.run(
        search.find_linkedin_profile(
            "Jane Doe",
            "Example Corp",
        )
    )

    assert result == "https://www.linkedin.com/in/janedoe"


def test_returns_none_when_no_linkedin_profile_found():
    search = ExternalSearch(
        client=FakeSearchClientWithoutLinkedIn()
    )

    import asyncio

    result = asyncio.run(
        search.find_linkedin_profile(
            "Jane Doe",
            "Example Corp",
        )
    )

    assert result is None


def test_returns_none_when_search_is_not_configured(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    search = ExternalSearch(client=None)

    import asyncio

    result = asyncio.run(
        search.find_linkedin_profile(
            "Jane Doe",
            "Example Corp",
        )
    )

    assert result is None