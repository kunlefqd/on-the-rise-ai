/**
 * MCP server registry for the TrendBaker CopilotKit agent.
 *
 * Env endpoints feed getConfiguredMcpServers(). Client registration via
 * useCopilotChat().setMcpServers() is currently unsupported in CopilotKit 1.63.x
 * (hook return omits the setter). Prefer BuiltInAgent / CopilotRuntime mcpServers
 * when wiring live Supabase MCP.
 */

export type McpServerId = "supabase" | "additional";

export type McpConnectionStatus = "not_connected" | "connected";

export interface McpServerConfig {
  endpoint: string;
  apiKey?: string;
}

export interface PlannedMcpServer {
  id: McpServerId;
  label: string;
  description: string;
  /** Env var that will hold the MCP SSE/HTTP endpoint URL. */
  endpointEnvVar: string;
}

export const PLANNED_MCP_SERVERS: PlannedMcpServer[] = [
  {
    id: "supabase",
    label: "Supabase MCP",
    description:
      "Approved database reads (e.g. public.vw_top_youtube_trends) via Supabase MCP.",
    endpointEnvVar: "NEXT_PUBLIC_SUPABASE_MCP_URL",
  },
  {
    id: "additional",
    label: "Additional MCP",
    description: "Second MCP server to be wired later.",
    endpointEnvVar: "NEXT_PUBLIC_ADDITIONAL_MCP_URL",
  },
];

function readEndpoint(envVar: string): string | undefined {
  const value = process.env[envVar]?.trim();
  return value || undefined;
}

/** Servers currently configured with an endpoint (passed to CopilotKit). */
export function getConfiguredMcpServers(): McpServerConfig[] {
  const servers: McpServerConfig[] = [];

  for (const planned of PLANNED_MCP_SERVERS) {
    const endpoint = readEndpoint(planned.endpointEnvVar);
    if (!endpoint) continue;
    servers.push({ endpoint });
  }

  return servers;
}

export function getMcpStatus(): Record<McpServerId, McpConnectionStatus> {
  return {
    supabase: readEndpoint("NEXT_PUBLIC_SUPABASE_MCP_URL")
      ? "connected"
      : "not_connected",
    additional: readEndpoint("NEXT_PUBLIC_ADDITIONAL_MCP_URL")
      ? "connected"
      : "not_connected",
  };
}
