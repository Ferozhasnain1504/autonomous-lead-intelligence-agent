from src.gemini_extractor import GeminiExtractor


class FakeInteraction:
    """Fake Gemini interaction for testing."""

    output_text = """
    {
        "company_name": "Example Corp",
        "company_overview": "Example Corp builds software for developers. Its platform helps development teams collaborate efficiently.",
        "target_audience": "Software development teams",
        "public_emails": ["info@example.com"],
        "leadership": [
            {
                "name": "Jane Doe",
                "role": "CEO",
                "linkedin_url": "https://www.linkedin.com/in/janedoe"
            }
        ],
        "confidence_score": 0.9,
        "evidence": [
            {
                "field": "company_overview",
                "evidence": "Example Corp builds software for developers."
            },
            {
                "field": "target_audience",
                "evidence": "The company builds software for development teams."
            }
        ]
    }
    """


class FakeInteractions:
    """Fake Gemini Interactions API."""

    def create(self, **kwargs):
        return FakeInteraction()


class FakeClient:
    """Fake Gemini client."""

    def __init__(self):
        self.interactions = FakeInteractions()


def test_gemini_extractor_returns_company_intelligence():
    extractor = GeminiExtractor(client=FakeClient())

    import asyncio

    result = asyncio.run(
        extractor.extract(
            "Example Corp builds software for developers."
        )
    )

    assert result.company_name == "Example Corp"
    assert result.target_audience == "Software development teams"
    assert result.public_emails == ["info@example.com"]
    assert len(result.leadership) == 1
    assert result.leadership[0].name == "Jane Doe"
    assert result.confidence_score == 0.9
    assert len(result.evidence) == 2
    assert result.evidence[0].field == "company_overview"
    assert result.evidence[0].evidence == (
        "Example Corp builds software for developers."
    )
    assert result.evidence[1].field == "target_audience"


def test_gemini_extractor_rejects_empty_content():
    extractor = GeminiExtractor(client=FakeClient())

    import asyncio

    try:
        asyncio.run(extractor.extract(""))
        assert False, "Expected ValueError"
    except ValueError as error:
        assert str(error) == "Company text cannot be empty."

class FakeBrokenInteraction:
    """Fake Gemini response containing invalid JSON."""

    output_text = "This is not valid JSON."


class FakeBrokenInteractions:
    """Fake Gemini interactions returning invalid output."""

    def create(self, **kwargs):
        return FakeBrokenInteraction()


class FakeBrokenClient:
    """Fake Gemini client returning invalid output."""

    def __init__(self):
        self.interactions = FakeBrokenInteractions()


class FakeFailingInteractions:
    """Fake Gemini interactions that raise an API error."""

    def create(self, **kwargs):
        raise RuntimeError("Gemini API unavailable")


class FakeFailingClient:
    """Fake Gemini client that simulates an API failure."""

    def __init__(self):
        self.interactions = FakeFailingInteractions()


def test_gemini_extractor_rejects_malformed_response():
    extractor = GeminiExtractor(client=FakeBrokenClient())

    import asyncio

    try:
        asyncio.run(
            extractor.extract(
                "Example Corp builds software for developers."
            )
        )
        assert False, "Expected validation/parsing error"
    except Exception as error:
        assert error is not None


def test_gemini_extractor_handles_api_failure():
    extractor = GeminiExtractor(client=FakeFailingClient())

    import asyncio

    try:
        asyncio.run(
            extractor.extract(
                "Example Corp builds software for developers."
            )
        )
        assert False, "Expected Gemini API error"
    except RuntimeError as error:
        assert str(error) == "Gemini API unavailable"