/**
 * Data access layer for dashboard trend summaries.
 *
 * Fetches from the FastAPI service in services/api/, which reads real
 * Supabase data (term_leaderboard / item_terms / items). Never falls back
 * to mock data on failure — callers surface the error instead, so a real
 * outage isn't mistaken for a working demo.
 */

import type { TrendDetail, TrendSummary } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchTrendSummaries(options?: {
  region?: string;
  limit?: number;
}): Promise<TrendSummary[]> {
  const url = new URL("/api/v1/trends", API_BASE);
  if (options?.region) url.searchParams.set("region", options.region);
  if (options?.limit) url.searchParams.set("limit", String(options.limit));

  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Failed to fetch trends (${res.status})`);
  }
  return res.json();
}

export async function fetchTrendDetail(
  trendName: string,
): Promise<TrendDetail | null> {
  const url = new URL(
    `/api/v1/trends/${encodeURIComponent(trendName)}`,
    API_BASE,
  );

  const res = await fetch(url.toString());
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`Failed to fetch trend detail (${res.status})`);
  }
  return res.json();
}

export function getDataLastUpdated(trends: TrendSummary[]): string | null {
  if (trends.length === 0) return null;
  return trends.reduce(
    (latest, trend) =>
      trend.last_updated > latest ? trend.last_updated : latest,
    trends[0].last_updated,
  );
}
