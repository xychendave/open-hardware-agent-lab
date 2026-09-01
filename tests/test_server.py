from __future__ import annotations

import pytest

from rebot_mhs_lab.server import (
    discover_devices,
    emergency_stop,
    plan_two_arm_handoff,
    read_device,
    write_device,
)


def test_tool_functions_expose_safe_defaults():
    discovered = discover_devices()
    assert discovered["devices"][0]["driver"] == "simulation"

    result = write_device(
        "rebot-dm",
        "position",
        {"shoulder_pan": 0.1},
    )
    assert result["ok"] is True
    assert result["result"]["applied"] is False


def test_tool_functions_return_structured_safety_errors():
    result = write_device(
        "rebot-dm",
        "position",
        {"shoulder_pan": 0.9},
        apply=True,
        confirmed=True,
    )
    assert result["ok"] is False
    assert result["error_type"] == "SafetyViolation"


def test_handoff_tool_never_moves_devices():
    before = read_device("rebot-dm")["result"]["sequence"]
    result = plan_two_arm_handoff()
    after = read_device("rebot-dm")["result"]["sequence"]
    assert result["ok"] is True
    assert result["result"]["mode"] == "dry-run only"
    assert after == before
