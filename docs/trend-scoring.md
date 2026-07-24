# Trend scoring

This document lists the planned scoring categories only. **Weights and the final scoring formula are not finalized** — `backend/src/trendbaker/trend_engine/scoring.py` is a placeholder interface, not an implementation.

Planned categories:

- **Velocity** — how fast a signal is growing over time.
- **Engagement** — the volume and quality of engagement (views, likes, comments, shares) relative to the item's reach.
- **Cross-source confirmation** — whether the same entity is appearing across multiple independent sources, not just one.
- **Recency** — how recently supporting items were published or captured.
- **Novelty** — how new or unexpected the entity is relative to prior observations.
- **Confidence** — an overall confidence signal derived from the categories above and the amount of supporting data.

The trend-scoring workstream owns turning these categories into an actual weighted formula. Until that's agreed, `trend_score` in [`contracts/trend-summary.schema.json`](../contracts/trend-summary.schema.json) should be treated as provisional wherever it's consumed.
