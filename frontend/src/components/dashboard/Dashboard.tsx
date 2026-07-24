"use client";

import { useState } from "react";
import {
  getDataLastUpdated,
  getTrendDetail,
  getTrendSummaries,
} from "@/lib/trends";
import type { TrendSummary } from "@/lib/types";
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

const TRENDS = getTrendSummaries();

interface DashboardProps {
  selectedTrend: string | null;
  onSelectTrend: (trendName: string) => void;
}

export function Dashboard({ selectedTrend, onSelectTrend }: DashboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>("trend_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const sortedTrends = sortTrends(TRENDS, sortKey, sortDir);
  const selectedSummary =
    TRENDS.find((t) => t.trend_name === selectedTrend) ?? null;
  const selectedDetail = selectedTrend
    ? getTrendDetail(selectedTrend)
    : null;

  const lastUpdated = getDataLastUpdated(TRENDS);
  const topTrend = [...TRENDS].sort((a, b) => b.trend_score - a.trend_score)[0];
  const avgScore =
    TRENDS.reduce((sum, t) => sum + t.trend_score, 0) / (TRENDS.length || 1);
  const highConfidenceCount = TRENDS.filter(
    (t) => t.confidence === "high",
  ).length;
  const totalVideos = TRENDS.reduce(
    (sum, t) => sum + t.supporting_video_count,
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

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-header__brand">
          <p className="dashboard-header__product">TrendBaker AI</p>
          <p className="dashboard-header__subtitle">
            YouTube-powered bakery trend intelligence
          </p>
        </div>
        <div className="dashboard-header__meta">
          <span className="status-pill">Demo data</span>
          <p className="dashboard-header__updated">
            Last updated: {formatTimestamp(lastUpdated)}
          </p>
        </div>
      </header>

      <div className="demo-banner" role="status">
        Demo data — awaiting live YouTube pipeline
      </div>

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
          hint={`${TRENDS.length} tracked trends`}
        />
        <KpiCard
          label="High confidence trends"
          value={String(highConfidenceCount)}
          hint="Confidence level = high"
        />
        <KpiCard
          label="Supporting videos"
          value={String(totalVideos)}
          hint="Across all demo trends"
        />
      </section>

      <div className="charts-grid">
        <TrendScoreBars trends={TRENDS} />
        <CategoryBreakdown trends={TRENDS} />
        <GrowthComparison trends={TRENDS} />
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
        <TrendDetailPanel trend={selectedSummary} detail={selectedDetail} />
      </div>
    </div>
  );
}
