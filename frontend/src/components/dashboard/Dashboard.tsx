"use client";

import { useState } from "react";
import { getDataLastUpdated } from "@/lib/trends";
import type { TrendDetail, TrendSummary } from "@/lib/types";
import { CategoryBreakdown } from "./CategoryBreakdown";
import { GrowthComparison } from "./GrowthComparison";
import { KpiCard } from "./KpiCard";
import { TrendDetailPanel } from "./TrendDetailPanel";
import { TrendScoreBars } from "./TrendScoreBars";
import { TrendTable, type SortKey } from "./TrendTable";

function sortTrends(
  trends: TrendSummary[],
  sortKey: SortKey,
  sortDir: "asc" | "desc",
): TrendSummary[] {
  const sorted = [...trends].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];

    if (typeof aVal === "string" && typeof bVal === "string") {
      return aVal.localeCompare(bVal);
    }

    const aNum =
      aVal === null || aVal === undefined
        ? Number.NEGATIVE_INFINITY
        : Number(aVal);
    const bNum =
      bVal === null || bVal === undefined
        ? Number.NEGATIVE_INFINITY
        : Number(bVal);
    return aNum - bNum;
  });

  return sortDir === "asc" ? sorted : sorted.reverse();
}

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString("en-CA", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  });
}

interface DashboardProps {
  trends: TrendSummary[];
  trendsLoading: boolean;
  trendsError: string | null;
  selectedTrend: string | null;
  onSelectTrend: (trendName: string) => void;
  selectedDetail: TrendDetail | null;
  detailLoading: boolean;
}

export function Dashboard({
  trends,
  trendsLoading,
  trendsError,
  selectedTrend,
  onSelectTrend,
  selectedDetail,
  detailLoading,
}: DashboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>("trend_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sortedTrends = sortTrends(trends, sortKey, sortDir);
  const selectedSummary =
    trends.find((t) => t.trend_name === selectedTrend) ?? null;

  const lastUpdated = getDataLastUpdated(trends);
  const topTrend = [...trends].sort((a, b) => b.trend_score - a.trend_score)[0];
  const avgScore =
    trends.reduce((sum, t) => sum + t.trend_score, 0) / (trends.length || 1);
  const highConfidenceCount = trends.filter(
    (t) => t.confidence === "high",
  ).length;
  const totalVideos = trends.reduce(
    (sum, t) => sum + t.supporting_video_count,
    0,
  );
  const totalBlogPosts = trends.reduce(
    (sum, t) => sum + t.supporting_blog_count,
    0,
  );

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((dir) => (dir === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDir(key === "trend_name" ? "asc" : "desc");
  };

  const statusLabel = trendsError
    ? "Data error"
    : trendsLoading
      ? "Loading…"
      : "Live data";

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-header__brand">
          <p className="dashboard-header__product">TrendBaker AI</p>
          <p className="dashboard-header__subtitle">
            YouTube- and blog-powered bakery trend intelligence
          </p>
        </div>
        <div className="dashboard-header__meta">
          <span className="status-pill">{statusLabel}</span>
          <p className="dashboard-header__updated">
            {lastUpdated
              ? `Last updated: ${formatTimestamp(lastUpdated)}`
              : "Last updated: —"}
          </p>
        </div>
      </header>

      {trendsError ? (
        <div className="demo-banner" role="status">
          Couldn&apos;t reach the trend API ({trendsError}). Is{" "}
          <code>uvicorn services.api.main:app</code> running on port 8000?
        </div>
      ) : trendsLoading ? (
        <div className="demo-banner" role="status">
          Loading live trend data…
        </div>
      ) : null}

      <section className="kpi-grid" aria-label="Key metrics">
        <KpiCard
          label="Top trend"
          value={topTrend?.trend_name ?? "—"}
          hint={
            topTrend
              ? `Score ${topTrend.trend_score} · +${topTrend.growth_7d ?? 0}% 7d`
              : undefined
          }
        />
        <KpiCard
          label="Average trend score"
          value={avgScore.toFixed(1)}
          hint={`${trends.length} tracked trends`}
        />
        <KpiCard
          label="High confidence trends"
          value={String(highConfidenceCount)}
          hint="Confidence level = high"
        />
        <KpiCard
          label="YouTube links"
          value={String(totalVideos)}
          hint="Across all tracked trends"
        />
        <KpiCard
          label="Blog links"
          value={String(totalBlogPosts)}
          hint="Across all tracked trends"
        />
      </section>

      <div className="charts-grid">
        <TrendScoreBars trends={trends} />
        <CategoryBreakdown trends={trends} />
        <GrowthComparison trends={trends} />
      </div>

      <div className="main-grid">
        <TrendTable
          trends={sortedTrends}
          selectedTrend={selectedTrend}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={handleSort}
          onSelect={onSelectTrend}
        />
        <TrendDetailPanel
          trend={selectedSummary}
          detail={selectedDetail}
          loading={detailLoading}
        />
      </div>
    </div>
  );
}
