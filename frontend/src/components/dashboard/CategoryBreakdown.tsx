import type { TrendCategory, TrendSummary } from "@/lib/types";

interface CategoryBreakdownProps {
  trends: TrendSummary[];
}

const CATEGORY_ORDER: TrendCategory[] = [
  "flavour",
  "ingredient",
  "format",
  "consumer_attribute",
];

function label(category: TrendCategory): string {
  return category.replaceAll("_", " ");
}

export function CategoryBreakdown({ trends }: CategoryBreakdownProps) {
  const counts = CATEGORY_ORDER.map((category) => ({
    category,
    count: trends.filter((t) => t.category === category).length,
  })).filter((item) => item.count > 0);

  const max = Math.max(...counts.map((c) => c.count), 1);

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Category breakdown</h2>
        <p className="panel__subtitle">How trends distribute by type</p>
      </div>
      <ul className="bar-list">
        {counts.map((item) => (
          <li key={item.category} className="bar-row">
            <span className="bar-row__label">{label(item.category)}</span>
            <div className="bar-row__track" aria-hidden="true">
              <div
                className="bar-row__fill bar-row__fill--category"
                style={{ width: `${(item.count / max) * 100}%` }}
              />
            </div>
            <span className="bar-row__value">{item.count}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
