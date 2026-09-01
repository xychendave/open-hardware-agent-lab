# DeepSeek Harness integration

## Why Harness is an adapter, not the hardware core

DeepSeek Harness is a developer-preview, plugin-based agent runtime. Its official `@deepseek-ai/dsh-mcp-client` plugin can connect to an external MCP server and register discovered tools under stable names such as `mcp__rebot__discover_devices`.

That gives this project a low-coupling first integration:

```text
DeepSeek model
  -> DeepSeek Harness tool/approval pipeline
  -> official dsh MCP client
  -> this repository's MCP server
  -> driver safety supervisor
  -> simulator or physical adapter
```

The driver remains independently testable and other agent runtimes can use it without DeepSeek.

## Local project configuration

The checked-in [.dsh/cordis.patch.yml](../.dsh/cordis.patch.yml) expects DeepSeek Harness to start with this repository as its current directory. It launches the Python MCP server over stdio.

1. Create the Python environment:

   ```bash
   uv sync --extra dev --python 3.12
   uv run pytest
   ```

2. Install or run DeepSeek Harness according to its official guide.

3. Install `@deepseek-ai/dsh-mcp-client` at the **same version** as the Harness host. Harness is in developer preview and mismatched release-candidate packages may be incompatible.

4. Start Harness from the repository root and ask it to call `mcp__rebot__discover_devices`.

5. Keep the first session read-only/dry-run. Do not install a real driver yet.

## Next native plugin

MCP is sufficient for the first milestone. A later project-specific Harness plugin should add defense in depth through the Harness tool pipeline:

- require an approval provider for live hardware tools;
- deny live tools outside an operator-opened session window;
- add per-device rate and concurrency guards;
- record immutable tool result/audit events;
- surface emergency-stop and stale-feedback state in every model turn;
- restrict the agent-visible tool catalog by task.

These harness guards improve user control and auditability but never replace driver-side enforcement.

## Versioning policy

- Pin a tested DeepSeek Harness version in deployment manifests.
- Treat tool names and JSON schemas as compatibility surfaces.
- Re-run the in-memory MCP tests and Harness discovery smoke test after every plugin update.
- Track upstream developer-preview breakage separately from device-driver regressions.

## Upstream references

- [DeepSeek Harness repository](https://github.com/deepseek-ai/deepseek-harness)
- [Official MCP client plugin](https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/mcp/mcp-client)
- [DeepSeek Harness Python SDK guide](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/python-sdk.md)
