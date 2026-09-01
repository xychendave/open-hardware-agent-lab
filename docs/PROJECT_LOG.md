# Project log

This is the public, reproducible engineering history. It records evidence and decisions, not private startup strategy.

## 2026-09-01 — Project framing

### Starting point

- Two Seeed/LeRobot-related arms are available, but their exact model pairing and hardware host are still to be confirmed.
- The development machine is an Apple Silicon Mac.
- No matching serial/CAN device was connected during the initial inspection.
- Anthropic announced the Model Hardware Standard research preview on 2026-08-27. Its public description covers standardized drivers, device discovery, simple read/write primitives, natural-language hardware metadata, safety limits and access through MCP/CLI/code. The specification and SDK are not yet public.

### Public-source review

- Seeed's B601-DM and B601-RS are both 6-DoF arms with one gripper and have LeRobot integrations.
- B601-DM uses a serial-bridge path in the published LeRobot example.
- B601-RS uses SocketCAN in the published follower example, making a Linux/Jetson hardware host the practical choice.
- DeepSeek Harness is an open-source developer-preview agent harness with an official MCP client plugin.

### Decisions

1. Build an independent, MHS-inspired device contract without claiming official compatibility.
2. Keep agent runtimes outside the hardware core.
3. Use MCP as the first adapter into Claude and DeepSeek Harness.
4. Default every public example to simulation and dry-run.
5. Delay the repository license decision to preserve startup licensing options.

### Implemented baseline

- Python 3.12 project managed by `uv`.
- Official MCP Python SDK 2.x.
- Simulated B601-DM and B601-RS descriptors.
- Discover/read/write slots with normalized positions.
- Explicit enable, apply and confirmation gates.
- Per-command step limit and latched emergency stop.
- Dry-run-only two-arm handoff plan.
- MCP tools plus one resource template.

### Verification

```text
uv run pytest
10 passed
```

An in-memory MCP client discovered five tools, read the device resource and successfully called `discover_devices`.

### Open questions

- Exact physical arm models: SO-ARM100/101 leader, B601-DM, B601-RS, or another pairing.
- Hardware-control host: Ubuntu x86, Jetson, Raspberry Pi or other.
- Camera inventory and mounting.
- Project license, contributor terms and possible patent strategy.
- Access to the official MHS research preview.

### Sources

- [Anthropic MHS announcement](https://www.anthropic.com/news/model-hardware-standard-research-preview)
- [MHS research-preview site](https://modelhardwarestandard.com/)
- [Seeed B601-DM guide](https://wiki.seeedstudio.com/cn/rebot_b601_dm_getting_started/)
- [Seeed B601-RS guide](https://wiki.seeedstudio.com/cn/rebot_b601_rs_getting_started/)
- [Seeed reBot repository](https://github.com/Seeed-Projects/reBot-DevArm)
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)

## 2026-09-01 — Public reference repository

- Created the public repository [`xychendave/open-hardware-agent-lab`](https://github.com/xychendave/open-hardware-agent-lab).
- Published the initial baseline at commit `0cf2692`.
- Enabled GitHub Issues, Discussions and private vulnerability reporting.
- Added public architecture, roadmap, safety policy, contributor boundary and three initial ADRs.
- Added a project-local DeepSeek Harness patch that connects the hardware server through the official MCP client plugin.
- Kept the repository unlicensed while the startup decides between open-source, open-core, dual-license and patent/licensing strategies.
