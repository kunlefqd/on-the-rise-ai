/**
 * Data access layer for dashboard trend summaries.
 *
 * TODO: Replace mock returns with a backend endpoint or Supabase-approved
 * read path (likely public.vw_top_youtube_trends via FastAPI or a reviewed
 * read-only policy). Do not connect the UI directly to Supabase yet.
 */

import {
  MOCK_LAST_UPDATED,
  MOCK_TREND_DETAILS,
  MOCK_TREND_SUMMARIES,
} from "./mock-trends";
import type { TrendDetail, TrendSummary } from "./types";

export function getTrendSummaries(): TrendSummary[] {
  // MOCK: returns static demo data — not live YouTube pipeline output.
  return [...MOCK_TREND_SUMMARIES];
}

export function getTrendDetail(trendName: string): TrendDetail | null {
  // MOCK: detail lookup from in-memory demo dataset.
  return MOCK_TREND_DETAILS[trendName] ?? null;
}

export function getDataLastUpdated(trends: TrendSummary[]): string {
  if (trends.length === 0) return MOCK_LAST_UPDATED;
  return trends.reduce((latest, trend) =>
    trend.last_updated > latest ? trend.last_updated : latest,
  trends[0].last_updated);
}
