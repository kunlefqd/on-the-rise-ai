import type { TrendSummary } from "@/lib/types";

interface GrowthComparisonProps {
  trends: TrendSummary[];
}

export function GrowthComparison({ trends }: GrowthComparisonProps) {
  const ranked = [...trends]
    .filter((t) => t.growth_7d !== null)
    .sort((a, b) => (b.growth_7d ?? 0) - (a.growth_7d ?? 0))
    .slice(0, 6);

  const max = Math.max(...ranked.map((t) => t.growth_7d ?? 0), 1);

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Growth comparison</h2>
        <p className="panel__subtitle">7-day growth leaders (demo)</p>
      </div>
      <ul className="bar-list">
        {ranked.map((trend) => (
          <li key={trend.trend_name} className="bar-row">
            <span className="bar-row__label">{trend.trend_name}</span>
            <div className="bar-row__track" aria-hidden="true">
              <div
                className="bar-row__fill bar-row__fill--growth"
                style={{
                  width: `${((trend.growth_7d ?? 0) / max) * 100}%`,
                }}
              />
            </div>
            <span className="bar-row__value">
              +{trend.growth_7d}%
              <span className="bar-row__sub">
                {" "}
                / 24h{" "}
                {trend.growth_24h === null
                  ? "—"
                  : `+${trend.growth_24h}%`}
              </span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
