"""Generic term tagging.

Matches existing `public.terms` rows (as `trendbaker.models.Term`) against
`items` text and inserts the results into `item_terms` as
`trendbaker.models.ItemTerm`. Works for any `source` in principle —
`item_terms` has no source-specific columns (see docs/db-schema.md) — but is
currently only invoked for source='blog' items, since YouTube items are
already tagged by a separate, independently-built implementation
(`tag_item()` in trendbaker.cli).

Never creates new terms: only matches against terms that already exist in
the database (via SupabaseRepository.get_terms(), a read). Never touches or
deletes existing item_terms rows (duplicate inserts are ignored at the
database level via the table's own primary key, not deleted or overwritten).
Does not run automatically against the live database — call
tag_blog_items() explicitly when approved.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from trendbaker.models import ItemTerm, Term

if TYPE_CHECKING:
    from trendbaker.repositories.supabase_repository import SupabaseRepository


def _term_pattern(label: str) -> re.Pattern[str]:
    """Case-insensitive whole-phrase match, e.g. 'pistachio' won't match
    inside 'pistachios' differently than intended, and multi-word labels
    like 'dubai chocolate' match as a phrase, not two separate words."""
    return re.compile(rf"\b{re.escape(label)}\b", re.IGNORECASE)


def match_terms(text: str, terms: list[Term]) -> list[tuple[int, str]]:
    """Return (term_id, category) pairs whose label matches `text`.

    One pair per category a matched term belongs to — matching item_terms'
    (item_id, term_id, category) grain, so a term filed under multiple
    categories (e.g. 'dubai chocolate' under both 'format' and 'flavour')
    produces one pair per category when matched, exactly as YouTube tagging
    already does. Terms without a persisted id (not yet written to the
    database) are skipped, since item_terms.term_id must reference a real row.
    """
    matches: list[tuple[int, str]] = []
    for term in terms:
        if term.id is None:
            continue
        if _term_pattern(term.label).search(text):
            for category in term.categories:
                matches.append((term.id, category))
    return matches


def tag_blog_items(repo: SupabaseRepository) -> int:
    """Tag all source='blog' items against existing public.terms.

    Combines each item's title + body, matches it against every existing
    term (case-insensitively), and inserts the resulting ItemTerm rows.
    Returns the number of new rows actually inserted (duplicates against
    already-tagged items are ignored, not counted). Does not execute unless
    called explicitly — see docs/blog-rss-sources.md for the approved
    command to run this live.
    """
    terms = repo.get_terms()
    items = repo.get_items_by_source("blog", fields="id,title,body")

    item_terms: list[ItemTerm] = []
    for item in items:
        combined = " ".join(part for part in (item.get("title"), item.get("body")) if part)
        if not combined:
            continue
        for term_id, category in match_terms(combined, terms):
            item_terms.append(ItemTerm(item_id=item["id"], term_id=term_id, category=category))

    return len(repo.insert_item_terms(item_terms))
