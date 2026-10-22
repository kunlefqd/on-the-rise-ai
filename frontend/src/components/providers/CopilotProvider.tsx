"use client";

import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

interface CopilotProviderProps {
  children: React.ReactNode;
}

/**
 * CopilotKit Cloud provider (free public API key).
 * Get a key at https://cloud.copilotkit.ai
 */
export function CopilotProvider({ children }: CopilotProviderProps) {
  const publicApiKey = process.env.NEXT_PUBLIC_COPILOT_CLOUD_API_KEY;

  if (!publicApiKey) {
    return <>{children}</>;
  }

  return (
    <CopilotKit publicApiKey={publicApiKey} showDevConsole={false}>
      {children}
    </CopilotKit>
  );
}
