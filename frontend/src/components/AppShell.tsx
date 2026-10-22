"use client";

import { useState } from "react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { getTrendSummaries } from "@/lib/trends";

const INITIAL_TREND =
  [...getTrendSummaries()].sort((a, b) => b.trend_score - a.trend_score)[0]
    ?.trend_name ?? null;

export function AppShell() {
  const [selectedTrend, setSelectedTrend] = useState<string | null>(
    INITIAL_TREND,
  );

  return (
    <div className="workspace">
      <ChatPanel selectedTrend={selectedTrend} />
      <main className="page">
        <Dashboard
          selectedTrend={selectedTrend}
          onSelectTrend={setSelectedTrend}
        />
      </main>
    </div>
  );
}
