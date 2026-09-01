# ADR 0003: Integrate DeepSeek Harness through MCP first

- Status: Accepted
- Date: 2026-09-01

## Context

DeepSeek Harness is plugin-based and already ships an official MCP client. The hardware contract also needs to work with Claude and other runtimes.

## Decision

Keep the Python hardware server independent and connect DeepSeek Harness through `@deepseek-ai/dsh-mcp-client`. Add a native Harness guard/audit plugin only after the MCP path is verified.

## Consequences

- The first integration is small and reversible.
- Harness updates do not force hardware-driver rewrites.
- Approval and audit can later be strengthened in both Harness and the driver.
- The project must pin tested developer-preview Harness versions.
