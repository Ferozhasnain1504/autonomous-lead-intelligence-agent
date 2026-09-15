import logging
from collections.abc import Awaitable, Callable


logger = logging.getLogger(__name__)


async def run_safely(
    operation: Callable[[], Awaitable],
    description: str,
):
    """
    Run an asynchronous operation without crashing the pipeline.

    Returns:
        The operation result when successful.
        None when the operation fails.
    """

    try:
        return await operation()

    except Exception as error:
        logger.warning(
            "Operation failed [%s]: %s",
            description,
            error,
        )
        return None