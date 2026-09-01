# ADR 0002: Simulation and dry-run are the defaults

- Status: Accepted
- Date: 2026-09-01

## Context

AI-generated hardware commands can damage equipment or injure people. Prompt instructions are not a reliable safety boundary.

## Decision

Start with simulated devices. Writes return proposals unless `apply=true`; motion also requires enabled actuators and `confirmed=true`. Real drivers must be selected explicitly and implement the same or stronger checks.

## Consequences

- Agent and protocol work can be tested without equipment.
- Accidental tool calls do not move hardware.
- Live demonstrations require deliberate setup and cannot reuse simulation coordinates.
