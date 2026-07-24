"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import type { TrendDetail, TrendSummary } from "@/lib/types";

interface DashboardCopilotContextProps {
  selectedTrend: string | null;
  trends: TrendSummary[];
  detail: TrendDetail | null;
}

/**
 * Makes real dashboard trend data (fetched by AppShell from services/api,
 * backed by Supabase) readable by the CopilotKit agent.
 */
export function DashboardCopilotContext({
  selectedTrend,
  trends,
  detail,
}: DashboardCopilotContextProps) {
  useCopilotReadable({
    description:
      "TrendBaker dashboard bakery trend summaries, sourced live from Supabase (term_leaderboard) via the FastAPI service. Includes trend scores, confidence, supporting video counts, and category. growth_24h/growth_7d are currently always null — not yet computed upstream.",
    value: trends,
  });

  useCopilotReadable({
    description:
      "Currently selected trend on the TrendBaker dashboard, including a data-derived summary and supporting video evidence when available.",
    value: {
      selectedTrend,
      detail,
    },
  });

  return null;
}
