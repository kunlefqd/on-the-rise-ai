"use client";

import { CopilotChat } from "@copilotkit/react-ui";
import { getMcpStatus } from "@/lib/chat/mcp-registry";
import { DashboardCopilotContext } from "./DashboardCopilotContext";
import { McpServerManager } from "./McpServerManager";

interface ChatPanelProps {
  selectedTrend?: string | null;
}

const INSTRUCTIONS = [
  "You are the TrendBaker AI assistant for FGF bakery R&D and product teams.",
  "Help users understand emerging bakery trends from the dashboard context you are given.",
  "Use dashboard readable context for trend scores, growth, confidence, categories, and evidence.",
  "When MCP servers are connected, use their tools for database / external data questions (including Supabase).",
  "If MCP tools are unavailable, say so clearly and answer from dashboard context when possible.",
  "Label demo/mock dashboard data when relevant. Be concise and decision-oriented.",
].join(" ");

export function ChatPanel({ selectedTrend = null }: ChatPanelProps) {
  const publicApiKey = process.env.NEXT_PUBLIC_COPILOT_CLOUD_API_KEY;
  const mcpStatus = getMcpStatus();
  const mcpConnected =
    mcpStatus.supabase === "connected" ||
    mcpStatus.additional === "connected";

  if (!publicApiKey) {
    return (
      <aside className="chat-panel" aria-label="TrendBaker assistant">
        <div className="chat-panel__header">
          <div>
            <p className="chat-panel__title">Assistant</p>
            <p className="chat-panel__subtitle">CopilotKit · setup required</p>
          </div>
          <span className="chat-panel__status">No API key</span>
        </div>
        <div className="chat-panel__setup">
          <p>
            Add your free CopilotKit Cloud public key to{" "}
            <code>frontend/.env</code> or <code>frontend/.env.local</code>:
          </p>
          <pre>NEXT_PUBLIC_COPILOT_CLOUD_API_KEY=ck_pub_...</pre>
          <p>
            Get a key at{" "}
            <a
              href="https://cloud.copilotkit.ai"
              target="_blank"
              rel="noopener noreferrer"
            >
              cloud.copilotkit.ai
            </a>
            , then restart the dev server.
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="chat-panel" aria-label="TrendBaker assistant">
      <div className="chat-panel__header">
        <div>
          <p className="chat-panel__title">Assistant</p>
          <p className="chat-panel__subtitle">CopilotKit agent · MCP ready</p>
        </div>
        <span className="chat-panel__status">
          {mcpConnected ? "MCP on" : "MCP offline"}
        </span>
      </div>

      {selectedTrend ? (
        <p className="chat-panel__context">
          Dashboard selection: <strong>{selectedTrend}</strong>
        </p>
      ) : (
        <p className="chat-panel__context">No trend selected on dashboard</p>
      )}

      <McpServerManager />
      <DashboardCopilotContext selectedTrend={selectedTrend} />

      <div className="chat-panel__copilot">
        <CopilotChat
          className="chat-panel__copilot-inner"
          instructions={INSTRUCTIONS}
          labels={{
            title: "TrendBaker Assistant",
            initial:
              "Ask about dashboard trends, growth, confidence, or evidence. MCP tools (including Supabase) can be added via env when ready.",
            placeholder: "Ask about trends or data…",
          }}
        />
      </div>
    </aside>
  );
}
