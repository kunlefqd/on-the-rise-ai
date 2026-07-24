"""Collector interface.

A collector fetches items from one external source and returns them as
``trendbaker.models.Item`` instances (which map 1:1 to the ``items`` table; see
docs/db-schema.md). Concrete collectors implement ``collect()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from trendbaker.models import Item


class Collector(ABC):
    """Base class for all data source collectors."""

    source_name: str

    @abstractmethod
    def collect(self) -> list[Item]:
        """Return a list of normalized items for this source."""
        raise NotImplementedError
