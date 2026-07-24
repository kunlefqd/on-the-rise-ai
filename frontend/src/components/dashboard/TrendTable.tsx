"use client";

import type { TrendSummary } from "@/lib/types";

export type SortKey =
  | "trend_score"
  | "growth_24h"
  | "growth_7d"
  | "supporting_video_count"
  | "trend_name";

interface TrendTableProps {
  trends: TrendSummary[];
  selectedTrend: string | null;
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
  onSelect: (trendName: string) => void;
}

function formatGrowth(value: number | null): string {
  if (value === null) return "—";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value}%`;
}

function categoryLabel(category: string): string {
  return category.replaceAll("_", " ");
}

export function TrendTable({
  trends,
  selectedTrend,
  sortKey,
  sortDir,
  onSort,
  onSelect,
}: TrendTableProps) {
  const sortIndicator = (key: SortKey) => {
    if (sortKey !== key) return "";
    return sortDir === "asc" ? " ↑" : " ↓";
  };

  return (
    <section className="panel">
      <div className="panel__header">
        <h2 className="panel__title">Top trends</h2>
        <p className="panel__subtitle">
          Ranked bakery signals from YouTube and blog sources
        </p>
      </div>
      <div className="table-wrap">
        <table className="trend-table">
          <thead>
            <tr>
              <th scope="col">Rank</th>
              <th scope="col">
                <button type="button" onClick={() => onSort("trend_name")}>
                  Trend{sortIndicator("trend_name")}
                </button>
              </th>
              <th scope="col">Category</th>
              <th scope="col">
                <button type="button" onClick={() => onSort("trend_score")}>
                  Trend score{sortIndicator("trend_score")}
                </button>
              </th>
              <th scope="col">
                <button type="button" onClick={() => onSort("growth_24h")}>
                  24h growth{sortIndicator("growth_24h")}
                </button>
              </th>
              <th scope="col">
                <button type="button" onClick={() => onSort("growth_7d")}>
                  7d growth{sortIndicator("growth_7d")}
                </button>
              </th>
              <th scope="col">Confidence</th>
              <th scope="col">
                <button
                  type="button"
                  onClick={() => onSort("supporting_video_count")}
                >
                  Videos / Blogs{sortIndicator("supporting_video_count")}
                </button>
              </th>
              <th scope="col">Region</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((trend, index) => {
              const isSelected = selectedTrend === trend.trend_name;
              return (
                <tr
                  key={trend.trend_name}
                  className={isSelected ? "is-selected" : undefined}
                  onClick={() => onSelect(trend.trend_name)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      onSelect(trend.trend_name);
                    }
                  }}
                  tabIndex={0}
                  aria-selected={isSelected}
                >
                  <td>{index + 1}</td>
                  <td className="trend-table__name">{trend.trend_name}</td>
                  <td>
                    <span className="category-chip">
                      {categoryLabel(trend.category)}
                    </span>
                  </td>
                  <td>
                    <strong>{trend.trend_score}</strong>
                  </td>
                  <td className={trend.growth_24h && trend.growth_24h > 0 ? "is-up" : undefined}>
                    {formatGrowth(trend.growth_24h)}
                  </td>
                  <td className={trend.growth_7d && trend.growth_7d > 0 ? "is-up" : undefined}>
                    {formatGrowth(trend.growth_7d)}
                  </td>
                  <td>
                    <span className={`confidence confidence--${trend.confidence}`}>
                      {trend.confidence}
                    </span>
                  </td>
                  <td>
                    {trend.supporting_video_count} / {trend.supporting_blog_count}
                  </td>
                  <td>{trend.query_region_code}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
