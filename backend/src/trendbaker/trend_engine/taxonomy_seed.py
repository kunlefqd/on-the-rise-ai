"""Bakery taxonomy seed/update utility.

Idempotently adds new canonical bakery terms to the existing public.terms
table (see docs/db-schema.md) — no migration, no schema change. Only ever
inserts/updates rows for the slugs in PROPOSED_TERMS via an upsert on
`slug`; never deletes any row, so pre-existing terms (e.g. the 10 seeded by
the YouTube/shared workstream) are left untouched. Categories use the same
array design and the same four values already in use: format, flavour,
ingredient, dietary. Does not run automatically — call seed_taxonomy()
explicitly when approved.

NOTE: trendbaker.taxonomy (built independently, for the YouTube CLI's query
generation + tagging) already lists 13 of these 20 terms under FORMATS/
FLAVOURS/INGREDIENTS. Checked programmatically against that module: 11 of
those 13 already agreed on category; 2 did not and have been reconciled here
to match trendbaker.taxonomy (the more established, already-in-production
list), rather than left to silently conflict on whichever seed runs last:
  - 'sourdough': was ['ingredient'] here, is ['format'] there -> now format.
  - 'black sesame': was ['flavour', 'ingredient'] here, is ['flavour'] there
    -> now flavour only.
The 7 terms genuinely novel to this list (absent from trendbaker.taxonomy
entirely) are: pizza, cream, chocolate, pastry, bread, high protein, gluten
free — the last two are notable because trendbaker.taxonomy has no
'dietary' category at all.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from trendbaker.models import Term

if TYPE_CHECKING:
    from trendbaker.repositories.supabase_repository import SupabaseRepository

_SLUG_INVALID_RE = re.compile(r"[^a-z0-9]+")


def slugify(label: str) -> str:
    """Lowercase, URL-safe, underscore-separated slug, e.g. 'Brown Butter' -> 'brown_butter'."""
    return _SLUG_INVALID_RE.sub("_", label.strip().lower()).strip("_")


# label -> categories (existing category values only: format, flavour,
# ingredient, dietary). Terms with more than one category (e.g. chocolate)
# preserve the same multi-category array design as the existing
# 'dubai chocolate' term.
PROPOSED_TERMS: list[dict[str, Any]] = [
    {"label": "pizza", "categories": ["format"]},
    {"label": "sourdough", "categories": ["format"]},  # matches trendbaker.taxonomy.FORMATS
    {"label": "croissant", "categories": ["format"]},
    {"label": "focaccia", "categories": ["format"]},
    {"label": "cream", "categories": ["ingredient"]},
    {"label": "chocolate", "categories": ["flavour", "ingredient"]},
    {"label": "brown butter", "categories": ["flavour", "ingredient"]},
    {"label": "matcha", "categories": ["flavour"]},
    {"label": "ube", "categories": ["flavour"]},
    {"label": "black sesame", "categories": ["flavour"]},  # matches trendbaker.taxonomy.FLAVOURS
    {"label": "cinnamon roll", "categories": ["format"]},
    {"label": "high protein", "categories": ["dietary"]},
    {"label": "gluten free", "categories": ["dietary"]},
    {"label": "muffin", "categories": ["format"]},
    {"label": "donut", "categories": ["format"]},
    {"label": "cupcake", "categories": ["format"]},
    {"label": "pastry", "categories": ["format"]},
    {"label": "bread", "categories": ["format"]},
    {"label": "brioche", "categories": ["format"]},
    {"label": "bagel", "categories": ["format"]},
]


def build_term_rows() -> list[Term]:
    """Return PROPOSED_TERMS as Term models (slug, label, categories)."""
    return [
        Term(slug=slugify(term["label"]), label=term["label"], categories=term["categories"])
        for term in PROPOSED_TERMS
    ]


def seed_taxonomy(repo: SupabaseRepository) -> int:
    """Idempotently upsert PROPOSED_TERMS into public.terms, on slug.

    Never deletes existing terms — only inserts new rows or updates rows for
    the slugs in PROPOSED_TERMS. Re-running with the same list is a no-op
    (upsert on slug). Does not execute unless called explicitly; see
    docs/blog-rss-sources.md or the calling report for the approved live
    command.
    """
    return len(repo.upsert_terms(build_term_rows()))
