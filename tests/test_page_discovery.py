from src.page_discovery import PageDiscovery


def test_relevance_score():
    discovery = PageDiscovery()

    score = discovery._calculate_relevance_score(
        url="https://example.com/about",
        text="About Us",
    )

    assert score > 0


def test_internal_link():
    discovery = PageDiscovery()

    assert discovery._is_internal_link(
        "https://example.com",
        "https://example.com/about",
    )

    assert not discovery._is_internal_link(
        "https://example.com",
        "https://linkedin.com/company/example",
    )


def test_duplicate_removal():
    discovery = PageDiscovery()

    candidates = [
        {"url": "https://example.com/about", "score": 10},
        {"url": "https://example.com/about", "score": 8},
        {"url": "https://example.com/team", "score": 9},
    ]

    result = discovery._remove_duplicates(candidates)

    assert result == [
        "https://example.com/about",
        "https://example.com/team",
    ]