# Ethical data policy

TrendBaker AI only collects permitted public bakery-related signals. This policy applies to every collector, current and future.

- **Prefer official APIs and RSS** over any other collection method.
- **Respect each source's terms of service.** If a source's ToS prohibits a form of collection, don't do it, regardless of technical feasibility.
- **Respect robots directives** (e.g. `robots.txt`) when collecting from a public website is otherwise permitted.
- **Respect API quotas and rate limits.** Do not attempt to work around throttling.
- **Do not bypass authentication, CAPTCHAs, or anti-bot protections.** If a source puts up a barrier, that is a signal collection is not permitted there.
- **Do not collect private content** (private videos, DMs, gated/members-only content, etc.).
- **Avoid unnecessary personal information.** Collect only what is needed for aggregate trend analysis — not individual creators' or commenters' personal data beyond what a public metric requires.
- **Store source URLs** for every collected item, for evidence and attribution.
- **Clearly label simulated or seeded data** so it is never mistaken for real collected signal.
- **Allow individual sources to be disabled** independently, so a problematic or rate-limited source can be turned off without affecting others.
- **Store only data required for trend analysis** — no speculative or "might be useful later" fields.

Every collector implementation should be reviewed against this list before it starts making real requests.
