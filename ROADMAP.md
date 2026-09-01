# Roadmap

The roadmap is organized by safety gates rather than calendar promises.

## Phase 0 — Reproducible simulation baseline ✅

- Two simulated Seeed reBot devices.
- MHS-inspired discovery, read and write slots.
- MCP tools and resource template.
- Dry-run by default, explicit enable/confirm/apply gates, step limits and latched emergency stop.
- In-memory MCP client verification and automated tests.

Exit evidence: `uv run pytest` passes and no real hardware dependency is installed.

## Phase 1 — Read-only real hardware

- Confirm exact arm models and controller host.
- Add separate B601-DM and B601-RS adapter packages.
- Discover ports/CAN interfaces without changing configuration.
- Read calibrated joint state, health and controller metadata.
- Capture device descriptors without storing unique serial numbers in Git.

Exit evidence: repeatable read-only sessions on each physical arm, with disconnect and stale-feedback tests.

## Phase 2 — Supervised single-arm motion

- Integrate calibrated joint limits and collision-aware workspaces.
- Add physical emergency-stop verification.
- Add low-speed deterministic waypoint execution.
- Require an on-site human confirmation for every live session.

Exit evidence: bounded single-joint and return-home tests on both arms.

## Phase 3 — DeepSeek Harness integration

- Validate the official MCP client bridge against this server.
- Add a hardware approval/guard plugin in the Harness tool pipeline.
- Persist audit events without persisting secrets or raw private video.
- Compare native tools and Code Mode for schema/token stability.

Exit evidence: DeepSeek Harness can discover and dry-run every hardware tool; unauthorized live motion is rejected below the harness layer.

## Phase 4 — Dual-arm reference task

- Calibrate a shared coordinate frame.
- Define exclusive zones and collision interlocks.
- Execute a deterministic object handoff with agent-level planning and controller-level motion.
- Add fault injection: dropped feedback, moved object, blocked path and emergency stop.

Exit evidence: repeated supervised handoffs with logs and no interlock violations.

## Phase 5 — Standards compatibility

- Track the official MHS publication or obtain authorized preview access.
- Build a clean adapter against the actual specification.
- Publish a conformance matrix that separates implemented, partial and unsupported behavior.
- Retain MCP, CLI and code interfaces as independent transports.

Exit evidence: tests against an official conformance suite or documented partner validation.
