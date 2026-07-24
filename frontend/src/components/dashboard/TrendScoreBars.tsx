import type { TrendSummary } from "@/lib/types";

interface TrendScoreBarsProps {
  trends: TrendSummary[];
}

export function TrendScoreBars({ trends }: TrendScoreBarsProps) {
  const top = [...trends]
    .sort((a, b) => b.trend_score - a.trend_score)
    .slice(0, 6);
  const max = Math.max(...top.map((t) => t.trend_score), 1);

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Top trend scores</h2>
        <p className="panel__subtitle">Relative strength of leading signals</p>
      </div>
      <ul className="bar-list">
        {top.map((trend) => (
          <li key={trend.trend_name} className="bar-row">
            <span className="bar-row__label">{trend.trend_name}</span>
            <div className="bar-row__track" aria-hidden="true">
              <div
                className="bar-row__fill bar-row__fill--score"
                style={{ width: `${(trend.trend_score / max) * 100}%` }}
              />
            </div>
            <span className="bar-row__value">{trend.trend_score}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
