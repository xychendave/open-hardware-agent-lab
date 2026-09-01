# ADR 0001: Build an independent device contract

- Status: Accepted
- Date: 2026-09-01

## Context

Anthropic has publicly described MHS but has not published its specification or SDK. Building against an imagined wire format would create false compatibility claims and expensive rework.

## Decision

Implement a small independent contract—discover, read and validated write—based only on public concepts. Label it `MHS-ready prototype`, not `MHS implementation`.

## Consequences

- Development and testing can begin immediately.
- The project remains model- and transport-agnostic.
- A future official MHS adapter will require explicit conformance work.
- Public documentation must distinguish inspiration from compatibility.
