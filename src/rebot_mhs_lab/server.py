from __future__ import annotations

import os
from typing import Any

from mcp.server import MCPServer

from .core import SafetyViolation, load_lab


mcp = MCPServer("reBot MHS-ready Lab")
lab = load_lab(os.environ.get("REBOT_DEVICE_CONFIG"))


def _tool_result(operation: str, function: Any) -> dict[str, Any]:
    try:
        return {"ok": True, "operation": operation, "result": function()}
    except (KeyError, SafetyViolation, TypeError, ValueError) as exc:
        return {
            "ok": False,
            "operation": operation,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


@mcp.tool()
def discover_devices() -> dict[str, Any]:
    """Discover the available arms, their slots, physical metadata, and safety limits."""

    return {
        "standard": "MHS-ready prototype (not the unreleased official MHS SDK)",
        "devices": lab.discover(),
    }


@mcp.tool()
def read_device(device_id: str, slot: str = "state") -> dict[str, Any]:
    """Read a device slot: state, position, enabled, or emergency_stop."""

    return _tool_result("read", lambda: lab.get(device_id).read(slot))


@mcp.tool()
def write_device(
    device_id: str,
    slot: str,
    value: Any,
    apply: bool = False,
    confirmed: bool = False,
) -> dict[str, Any]:
    """Write one device slot.

    Calls are dry-run by default. Applying motion requires enabled actuators plus
    both apply=true and confirmed=true. Emergency stop always disables motion.
    """

    return _tool_result(
        "write",
        lambda: lab.get(device_id).write(
            slot,
            value,
            apply=apply,
            confirmed=confirmed,
        ),
    )


@mcp.tool()
def emergency_stop(device_id: str) -> dict[str, Any]:
    """Latch the emergency stop immediately and disable the selected arm."""

    return _tool_result(
        "emergency_stop",
        lambda: lab.get(device_id).write(
            "emergency_stop",
            True,
            apply=True,
            confirmed=True,
        ),
    )


@mcp.tool()
def plan_two_arm_handoff(
    from_device: str = "rebot-dm",
    to_device: str = "rebot-rs",
) -> dict[str, Any]:
    """Build a dry-run plan for a two-arm object handoff; never moves hardware."""

    return _tool_result(
        "plan_two_arm_handoff",
        lambda: lab.handoff_plan(from_device, to_device),
    )


@mcp.resource("mhs-prototype://devices/{device_id}")
def device_descriptor(device_id: str) -> dict[str, Any]:
    """Return the MHS-style descriptor for one device."""

    return lab.get(device_id).discover()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
