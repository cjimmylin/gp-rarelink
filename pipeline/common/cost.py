"""Token usage → USD, using the price table in configs/prices.yaml.

Usage dicts follow the Anthropic API ``usage`` object:
``input_tokens``, ``output_tokens``, ``cache_read_input_tokens``,
``cache_creation_input_tokens``. Missing keys count as zero. A non-zero
component whose price is null in the table raises, so an unverified price can
never silently become a $0 line in BUDGET.md.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRICES = REPO_ROOT / "configs" / "prices.yaml"

USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)

_PRICE_FOR_KEY = {
    "input_tokens": "input",
    "output_tokens": "output",
    "cache_read_input_tokens": "cache_read",
    "cache_creation_input_tokens": "cache_write_5m",
}


class PriceMissing(ValueError):
    """A usage component has no price in the table."""


@dataclass
class PriceTable:
    models: dict[str, dict[str, Any]]
    source: str
    read_on: str
    verified_on: str | None
    path: Path

    @classmethod
    def load(cls, path: Path | str = DEFAULT_PRICES) -> "PriceTable":
        path = Path(path)
        with path.open() as fh:
            raw = yaml.safe_load(fh)
        return cls(
            models=raw["models"],
            source=raw.get("source", ""),
            read_on=str(raw.get("read_on", "")),
            verified_on=raw.get("verified_on"),
            path=path,
        )

    def cost_usd(self, model: str, usage: dict[str, int]) -> float:
        """Dollar cost of one request's usage for ``model``."""
        if model not in self.models:
            raise PriceMissing(f"no prices for model {model!r} in {self.path}")
        prices = self.models[model]
        unknown = set(usage) - set(USAGE_KEYS)
        if unknown:
            raise ValueError(f"unknown usage keys {sorted(unknown)}; expected {USAGE_KEYS}")
        total = 0.0
        for key in USAGE_KEYS:
            n = int(usage.get(key, 0) or 0)
            if n == 0:
                continue
            price = prices.get(_PRICE_FOR_KEY[key])
            if price is None:
                raise PriceMissing(
                    f"{model}: price for {_PRICE_FOR_KEY[key]!r} is null in {self.path}; "
                    "verify it on the live pricing page before pricing this usage"
                )
            total += n / 1_000_000 * float(price)
        threshold = prices.get("long_prompt_threshold_tokens")
        if threshold and int(usage.get("input_tokens", 0) or 0) > int(threshold):
            warnings.warn(
                f"{model}: request input exceeds {threshold} tokens; the long-prompt tier "
                "applies and is not modelled here. Price it by hand.",
                stacklevel=2,
            )
        return round(total, 6)


@dataclass
class UsageTotals:
    """Accumulates usage across many requests and prices the sum."""

    model: str
    table: PriceTable = field(default_factory=PriceTable.load)
    n_requests: int = 0
    usage: dict[str, int] = field(default_factory=lambda: {k: 0 for k in USAGE_KEYS})
    cost_usd: float = 0.0

    def add(self, usage: dict[str, int]) -> float:
        cost = self.table.cost_usd(self.model, usage)
        for key in USAGE_KEYS:
            self.usage[key] += int(usage.get(key, 0) or 0)
        self.n_requests += 1
        self.cost_usd = round(self.cost_usd + cost, 6)
        return cost

    def cache_hit_rate(self) -> float | None:
        """Share of input tokens served from cache (None if no input yet)."""
        read = self.usage["cache_read_input_tokens"]
        total = read + self.usage["input_tokens"] + self.usage["cache_creation_input_tokens"]
        return None if total == 0 else round(read / total, 4)
