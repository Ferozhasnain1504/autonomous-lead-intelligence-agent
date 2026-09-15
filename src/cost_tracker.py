from dataclasses import dataclass


@dataclass
class UsageStats:
    """Track token usage and estimated API cost."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_requests: int = 0
    estimated_cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Return total input and output tokens."""
        return self.input_tokens + self.output_tokens

    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        input_cost_per_million: float = 0.0,
        output_cost_per_million: float = 0.0,
    ) -> None:
        """Add token usage and calculate estimated cost."""

        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_requests += 1

        input_cost = (
            input_tokens / 1_000_000
        ) * input_cost_per_million

        output_cost = (
            output_tokens / 1_000_000
        ) * output_cost_per_million

        self.estimated_cost_usd += input_cost + output_cost