"use client";

import { useEffect, useState } from "react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { fetchTrendDetail, fetchTrendSummaries } from "@/lib/trends";
import type { TrendDetail, TrendSummary } from "@/lib/types";

export function AppShell() {
  const [trends, setTrends] = useState<TrendSummary[]>([]);
  const [trendsLoading, setTrendsLoading] = useState(true);
  const [trendsError, setTrendsError] = useState<string | null>(null);

  const [selectedTrend, setSelectedTrend] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<TrendDetail | null>(
    null,
  );
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchTrendSummaries()
      .then((data) => {
        if (cancelled) return;
        setTrends(data);
        setTrendsError(null);
        // Safe to select unconditionally: trends starts empty, so no row
        // exists for the user to click before this first load resolves.
        const top = [...data].sort((a, b) => b.trend_score - a.trend_score)[0];
        if (top) {
          setSelectedTrend(top.trend_name);
          setDetailLoading(true);
        }
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setTrendsError(err.message);
      })
      .finally(() => {
        if (!cancelled) setTrendsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedTrend) return;
    let cancelled = false;
    fetchTrendDetail(selectedTrend)
      .then((data) => {
        if (!cancelled) setSelectedDetail(data);
      })
      .catch(() => {
        if (!cancelled) setSelectedDetail(null);
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedTrend]);

  const handleSelectTrend = (trendName: string) => {
    setSelectedTrend(trendName);
    setDetailLoading(true);
  };

  return (
    <div className="workspace">
      <ChatPanel
        selectedTrend={selectedTrend}
        trends={trends}
        selectedDetail={selectedDetail}
      />
      <main className="page">
        <Dashboard
          trends={trends}
          trendsLoading={trendsLoading}
          trendsError={trendsError}
          selectedTrend={selectedTrend}
          onSelectTrend={handleSelectTrend}
          selectedDetail={selectedDetail}
          detailLoading={detailLoading}
        />
      </main>
    </div>
  );
}
