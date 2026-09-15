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
        "confidence_score": 0.9
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


def test_gemini_extractor_rejects_empty_content():
    extractor = GeminiExtractor(client=FakeClient())

    import asyncio

    try:
        asyncio.run(extractor.extract(""))
        assert False, "Expected ValueError"
    except ValueError as error:
        assert str(error) == "Company text cannot be empty."