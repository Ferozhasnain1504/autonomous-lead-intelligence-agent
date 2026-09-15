import pytest

from src.safe_runner import run_safely


@pytest.mark.asyncio
async def test_run_safely_returns_successful_result():
    async def successful_operation():
        return "success"

    result = await run_safely(
        successful_operation,
        "successful test",
    )

    assert result == "success"


@pytest.mark.asyncio
async def test_run_safely_returns_none_when_operation_fails():
    async def failing_operation():
        raise RuntimeError("Something went wrong")

    result = await run_safely(
        failing_operation,
        "failing test",
    )

    assert result is None