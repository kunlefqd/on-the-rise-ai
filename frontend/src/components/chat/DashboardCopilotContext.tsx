"use client";

import { useCopilotReadable } from "@copilotkit/react-core";
import { getTrendDetail, getTrendSummaries } from "@/lib/trends";

interface DashboardCopilotContextProps {
  selectedTrend: string | null;
}

/**
 * Makes dashboard trend data readable by the CopilotKit agent.
 */
export function DashboardCopilotContext({
  selectedTrend,
}: DashboardCopilotContextProps) {
  const trends = getTrendSummaries();
  const detail = selectedTrend ? getTrendDetail(selectedTrend) : null;

  useCopilotReadable({
    description:
      "TrendBaker dashboard bakery trend summaries (demo data until live YouTube pipeline is connected). Includes trend scores, growth, confidence, supporting video counts, and region.",
    value: trends,
  });

  useCopilotReadable({
    description:
      "Currently selected trend on the TrendBaker dashboard, including R&D opportunity and supporting video evidence when available.",
    value: {
      selectedTrend,
      detail,
    },
  });

  return null;
}
