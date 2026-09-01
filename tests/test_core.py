from __future__ import annotations

import pytest

from rebot_mhs_lab import SafetyViolation, load_lab


@pytest.fixture()
def lab():
    return load_lab()


def test_discovers_both_rebot_models(lab):
    descriptors = lab.discover()
    assert [item["device_id"] for item in descriptors] == ["rebot-dm", "rebot-rs"]
    assert descriptors[0]["model"] == "reBot Arm B601-DM"
    assert descriptors[1]["model"] == "reBot Arm B601-RS"
    assert descriptors[0]["mhs_compatibility"]["status"] == "prototype"


def test_position_write_is_dry_run_by_default(lab):
    arm = lab.get("rebot-dm")
    result = arm.write("position", {"shoulder_pan": 0.1})
    assert result["applied"] is False
    assert arm.read("position")["shoulder_pan"] == 0.0


def test_motion_requires_enable_and_confirmation(lab):
    arm = lab.get("rebot-dm")
    with pytest.raises(SafetyViolation, match="disabled"):
        arm.write("position", {"shoulder_pan": 0.1}, apply=True, confirmed=True)

    arm.write("enabled", True, apply=True, confirmed=True)
    with pytest.raises(SafetyViolation, match="confirmed=true"):
        arm.write("position", {"shoulder_pan": 0.1}, apply=True)

    result = arm.write(
        "position",
        {"shoulder_pan": 0.1},
        apply=True,
        confirmed=True,
    )
    assert result["applied"] is True
    assert arm.read("position")["shoulder_pan"] == 0.1


def test_large_step_is_rejected(lab):
    arm = lab.get("rebot-rs")
    with pytest.raises(SafetyViolation, match="per-command limit"):
        arm.write("position", {"elbow_flex": 0.5})


def test_emergency_stop_latches_and_disables(lab):
    arm = lab.get("rebot-rs")
    arm.write("enabled", True, apply=True, confirmed=True)
    arm.write("emergency_stop", True, apply=True)
    assert arm.read("emergency_stop") is True
    assert arm.read("enabled") is False

    with pytest.raises(SafetyViolation, match="latched"):
        arm.write("enabled", True, apply=True, confirmed=True)

    with pytest.raises(SafetyViolation, match="confirmed=true"):
        arm.write("emergency_stop", False, apply=True)


def test_handoff_plan_is_bounded_and_dry_run(lab):
    plan = lab.handoff_plan("rebot-dm", "rebot-rs")
    assert plan["mode"] == "dry-run only"
    assert len(plan["steps"]) == 7
    assert lab.get("rebot-dm").read("state")["sequence"] == 0
    assert lab.get("rebot-rs").read("state")["sequence"] == 0
