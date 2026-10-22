"use client";

import { useEffect } from "react";
import { useCopilotChat } from "@copilotkit/react-core";
import { getConfiguredMcpServers } from "@/lib/chat/mcp-registry";

/**
 * Registers MCP server endpoints with CopilotKit when the client API supports it.
 *
 * In @copilotkit/react-core@1.63.x, useCopilotChat() types still mention setMcpServers
 * but useCopilotChatInternal no longer returns it — so we guard before calling.
 * Until MCP env URLs are set and a supported registration path is available
 * (e.g. BuiltInAgent mcpServers / runtime), this is a no-op.
 */
export function McpServerManager() {
  const chat = useCopilotChat();
  const setMcpServers =
    typeof chat.setMcpServers === "function" ? chat.setMcpServers : null;

  useEffect(() => {
    if (!setMcpServers) return;
    setMcpServers(getConfiguredMcpServers());
  }, [setMcpServers]);

  return null;
}
