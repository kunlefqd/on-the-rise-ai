"""Command-line runner for collectors.

Generates a bounded set of search queries from the seed taxonomy, runs the
YouTube collector, tags each item against the taxonomy, prints what came back,
and (optionally) loads it into Supabase.

Quota safety is built in: every run prints an estimated quota cost, and a run
that would exceed ``--max-units`` is refused unless ``--force`` is given.
``--dry-run`` prints the queries and estimate without calling the API at all.

Run without reinstalling via:  python -m trendbaker.cli --dry-run
Or, once installed, via the console script:  trendbaker-collect --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from trendbaker.collectors.youtube import YouTubeAPIError, YouTubeCollector
from trendbaker.models import Item, ItemTerm, Term
from trendbaker.taxonomy import (
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_MAX_PER_QUERY,
    DEFAULT_ORDER,
    DEFAULT_REGIONS,
    FLAVOURS,
    FORMATS,
    SEED_CATEGORIES,
)

_SEARCH_UNIT_COST = 100  # search.list costs 100 units per call
_DEFAULT_MODIFIERS = ["recipe", "trend"]  # matches the plan's 24-query default
_DEFAULT_TERMS_PER_CATEGORY = 6
_DEFAULT_MAX_UNITS = 5000  # ~half the standard 10k daily budget

# term text -> the categories it belongs to (a term can span several, e.g.
# "dubai chocolate" is both a format and a flavour).
_TERM_CATEGORIES: dict[str, list[str]] = {}
for _category, _terms in SEED_CATEGORIES.items():
    for _term in _terms:
        _TERM_CATEGORIES.setdefault(_term, [])
        if _category not in _TERM_CATEGORIES[_term]:
            _TERM_CATEGORIES[_term].append(_category)


# ---------- query generation ----------

def build_queries(terms_per_category: int, modifiers: list[str]) -> list[str]:
    """Cross the first N formats + flavours with each modifier (deduped)."""
    seed_terms = FORMATS[:terms_per_category] + FLAVOURS[:terms_per_category]
    queries = [f"{term} {modifier}" for term in seed_terms for modifier in modifiers]
    return list(dict.fromkeys(queries))  # dedupe, preserve order


# ---------- tagging ----------

def _slug(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", term.lower()).strip("_")


def tag_item(item: Item) -> dict[str, list[str]]:
    """Return {category: [matched terms]} for an item, whole-phrase, case-insensitive."""
    tags = item.raw.get("tags", []) if item.raw else []
    haystack = " ".join(
        part for part in [item.title or "", item.body or "", " ".join(tags)] if part
    ).lower()
    matches: dict[str, list[str]] = {}
    for category, terms in SEED_CATEGORIES.items():
        hits = [t for t in terms if re.search(rf"\b{re.escape(t)}\b", haystack)]
        if hits:
            matches[category] = hits
    return matches


# ---------- output ----------

def _print_estimate(queries: list[str], regions: list[str | None], max_units: int) -> int:
    n_regions = len(regions)
    search_units = len(queries) * n_regions * _SEARCH_UNIT_COST
    hydrate_units = len(queries) * n_regions  # worst case ~1 hydrate batch/query
    est = search_units + hydrate_units
    region_label = ", ".join(r or "global" for r in regions)
    print(
        f"Quota estimate: {len(queries)} queries x {n_regions} region(s) "
        f"[{region_label}] ~= {est:,} units "
        f"({search_units:,} search + {hydrate_units:,} hydrate)"
    )
    return est


def _print_items(items: list[Item], show: int) -> None:
    print(f"\nCollected {len(items)} item(s). Showing up to {show}:\n")
    for it in items[:show]:
        published = it.published_at.date().isoformat() if it.published_at else "?"
        print(f"  {it.title or '(no title)'}")
        print(f"    {it.url}")
        print(
            f"    {it.author} | {published} | "
            f"{it.views:,} views, {it.likes:,} likes, {it.comments_count:,} comments"
        )
        tags = tag_item(it)
        if tags:
            summary = "; ".join(f"{cat}: {', '.join(terms)}" for cat, terms in tags.items())
            print(f"    matched -> {summary}")
        print()


def _dump_jsonl(items: list[Item], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for it in items:
            fh.write(it.model_dump_json(exclude_none=True) + "\n")
    print(f"Wrote {len(items)} record(s) to {path}")


# ---------- load ----------

def load_to_supabase(items: list[Item]) -> None:
    """Tag items and upsert terms/items/item_terms, then refresh the rollup."""
    from trendbaker.repositories.supabase_repository import SupabaseRepository

    tagged = [(item, tag_item(item)) for item in items]

    # 1. unique matched terms -> Term rows
    matched_terms = {
        term
        for _, matches in tagged
        for terms in matches.values()
        for term in terms
    }
    terms = [
        Term(slug=_slug(t), label=t, categories=_TERM_CATEGORIES[t]) for t in matched_terms
    ]

    repo = SupabaseRepository()
    term_rows = repo.upsert_terms(terms)
    slug_to_id = {row["slug"]: row["id"] for row in term_rows}

    item_rows = repo.upsert_items(items)
    key_to_id = {(row["source"], row["source_id"]): row["id"] for row in item_rows}

    item_terms: list[ItemTerm] = []
    for item, matches in tagged:
        item_id = key_to_id.get((item.source, item.source_id))
        if item_id is None:
            continue
        for category, terms_in_cat in matches.items():
            for term in terms_in_cat:
                item_terms.append(
                    ItemTerm(item_id=item_id, term_id=slug_to_id[_slug(term)], category=category)
                )

    repo.insert_item_terms(item_terms)
    repo.refresh_term_week_stats()
    print(
        f"Loaded: {len(term_rows)} terms, {len(item_rows)} items, "
        f"{len(item_terms)} item_terms; refreshed term_week_stats."
    )


# ---------- entrypoint ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trendbaker-collect", description=__doc__)
    p.add_argument("--source", default="youtube", choices=["youtube"], help="Data source.")
    p.add_argument("--queries", nargs="+", help="Override the generated query set entirely.")
    p.add_argument(
        "--terms-per-category",
        type=int,
        default=_DEFAULT_TERMS_PER_CATEGORY,
        help="How many seed formats + flavours to use when generating queries.",
    )
    p.add_argument("--modifiers", nargs="+", default=_DEFAULT_MODIFIERS, help="Query modifiers.")
    p.add_argument("--days", type=int, default=DEFAULT_LOOKBACK_DAYS, help="Lookback window.")
    p.add_argument(
        "--max-per-query", type=int, default=DEFAULT_MAX_PER_QUERY, help="Results/query."
    )
    p.add_argument("--order", default=DEFAULT_ORDER, help="relevance|date|viewCount|rating.")
    p.add_argument(
        "--regions",
        nargs="*",
        default=list(DEFAULT_REGIONS),
        help="ISO region codes; pass with no value for a single global pass.",
    )
    p.add_argument(
        "--max-units", type=int, default=_DEFAULT_MAX_UNITS, help="Refuse runs above this."
    )
    p.add_argument("--force", action="store_true", help="Run even if over --max-units.")
    p.add_argument("--dry-run", action="store_true", help="Print queries + estimate, no API call.")
    p.add_argument("--show", type=int, default=5, help="How many collected items to print.")
    p.add_argument("--dump", type=Path, help="Write collected items to this JSONL path.")
    p.add_argument("--load", action="store_true", help="Load results into Supabase.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    queries = args.queries or build_queries(args.terms_per_category, args.modifiers)
    regions: list[str | None] = args.regions if args.regions else [None]

    est = _print_estimate(queries, regions, args.max_units)

    if est > args.max_units and not args.force:
        print(
            f"\nRefusing: estimate {est:,} exceeds --max-units {args.max_units:,}. "
            f"Narrow the run (fewer queries/regions) or pass --force.",
            file=sys.stderr,
        )
        return 2

    if args.dry_run:
        print(f"\nDry run — {len(queries)} queries, no API call:")
        for q in queries:
            print(f"  - {q}")
        return 0

    items: list[Item] = []
    try:
        for region in regions:
            collector = YouTubeCollector(
                queries,
                days=args.days,
                max_per_query=args.max_per_query,
                order=args.order,
                region=region,
            )
            items.extend(collector.collect())
    except YouTubeAPIError as exc:
        print(f"\nYouTube API error: {exc}", file=sys.stderr)
        return 1

    _print_items(items, args.show)

    if args.dump:
        _dump_jsonl(items, args.dump)

    if args.load:
        load_to_supabase(items)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
