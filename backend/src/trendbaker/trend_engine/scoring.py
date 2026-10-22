"""Trend scoring interface.

PLACEHOLDER — the scoring formula and category weights are not finalized.
See docs/trend-scoring.md for the planned scoring categories (velocity,
engagement, cross-source confirmation, recency, novelty, confidence).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TrendScorer(ABC):
    """Base interface for computing a trend-summary score from raw signals."""

    @abstractmethod
    def score(self, entity: str, items: list[dict[str, Any]]) -> float:
        """Return a trend score for `entity` given its supporting items."""
        raise NotImplementedError
