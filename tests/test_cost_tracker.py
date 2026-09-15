from src.cost_tracker import UsageStats


def test_total_tokens():
    stats = UsageStats()

    stats.add_usage(
        input_tokens=100,
        output_tokens=50,
    )

    assert stats.input_tokens == 100
    assert stats.output_tokens == 50
    assert stats.total_tokens == 150
    assert stats.total_requests == 1


def test_multiple_usage_entries():
    stats = UsageStats()

    stats.add_usage(
        input_tokens=100,
        output_tokens=50,
    )

    stats.add_usage(
        input_tokens=200,
        output_tokens=100,
    )

    assert stats.input_tokens == 300
    assert stats.output_tokens == 150
    assert stats.total_tokens == 450
    assert stats.total_requests == 2


def test_estimated_cost():
    stats = UsageStats()

    stats.add_usage(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        input_cost_per_million=1.0,
        output_cost_per_million=2.0,
    )

    assert stats.estimated_cost_usd == 3.0