"""Collector interface.

A collector fetches items from one external source and yields them as
normalized-content dicts (see contracts/normalized-content.schema.json at the
repo root). Concrete collectors implement `collect()`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Collector(ABC):
    """Base class for all data source collectors."""

    source_name: str

    @abstractmethod
    def collect(self) -> list[dict[str, Any]]:
        """Return a list of normalized-content items for this source."""
        raise NotImplementedError
