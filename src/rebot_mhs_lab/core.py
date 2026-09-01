from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


JOINT_NAMES = (
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_yaw",
    "wrist_roll",
    "gripper",
)


class SafetyViolation(ValueError):
    """Raised when a command violates a device-level safety constraint."""


@dataclass(frozen=True)
class SafetyPolicy:
    normalized_position_min: float = -1.0
    normalized_position_max: float = 1.0
    max_delta_per_command: float = 0.15
    require_explicit_enable: bool = True
    require_confirmation_for_motion: bool = True
    start_disabled: bool = True


@dataclass(frozen=True)
class DeviceDescriptor:
    device_id: str
    manufacturer: str
    model: str
    driver: str
    connection: str
    degrees_of_freedom: int
    payload_kg: float
    weight_kg: float
    supply_voltage_v: float
    natural_language_tags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        descriptor = asdict(self)
        descriptor["natural_language_tags"] = list(self.natural_language_tags)
        descriptor["slots"] = {
            "state": "read-only device state",
            "position": "read/write normalized joint positions",
            "enabled": "read/write actuator enable state",
            "emergency_stop": "read/write latched emergency stop",
        }
        descriptor["mhs_compatibility"] = {
            "status": "prototype",
            "note": "MHS is not public yet; this mirrors its announced discovery/read/write/safety concepts.",
        }
        return descriptor


@dataclass
class ArmState:
    positions: dict[str, float] = field(
        default_factory=lambda: {joint: 0.0 for joint in JOINT_NAMES}
    )
    enabled: bool = False
    emergency_stop: bool = False
    object_held: bool = False
    sequence: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "positions": dict(self.positions),
            "enabled": self.enabled,
            "emergency_stop": self.emergency_stop,
            "object_held": self.object_held,
            "sequence": self.sequence,
        }


class SimulatedArmDriver:
    """A deterministic driver with hardware-style interlocks.

    The interface intentionally stays small: discover the device, read a named
    slot, or write a named slot. An official MHS adapter can later wrap these
    same operations when the preview SDK is available.
    """

    def __init__(self, descriptor: DeviceDescriptor, safety: SafetyPolicy):
        if descriptor.degrees_of_freedom != len(JOINT_NAMES):
            raise ValueError(
                f"{descriptor.device_id} declares {descriptor.degrees_of_freedom} DoF; "
                f"this demo expects {len(JOINT_NAMES)}"
            )
        self.descriptor = descriptor
        self.safety = safety
        self.state = ArmState(enabled=not safety.start_disabled)

    def discover(self) -> dict[str, Any]:
        result = self.descriptor.as_dict()
        result["safety"] = asdict(self.safety)
        return result

    def read(self, slot: str) -> Any:
        if slot == "state":
            return self.state.as_dict()
        if slot == "position":
            return dict(self.state.positions)
        if slot == "enabled":
            return self.state.enabled
        if slot == "emergency_stop":
            return self.state.emergency_stop
        raise KeyError(f"Unknown readable slot: {slot}")

    def write(
        self,
        slot: str,
        value: Any,
        *,
        apply: bool = False,
        confirmed: bool = False,
    ) -> dict[str, Any]:
        if slot == "position":
            return self._write_position(value, apply=apply, confirmed=confirmed)
        if slot == "enabled":
            return self._write_enabled(value, apply=apply, confirmed=confirmed)
        if slot == "emergency_stop":
            return self._write_emergency_stop(value, apply=apply, confirmed=confirmed)
        raise KeyError(f"Unknown writable slot: {slot}")

    def _write_position(
        self,
        value: Any,
        *,
        apply: bool,
        confirmed: bool,
    ) -> dict[str, Any]:
        if not isinstance(value, Mapping) or not value:
            raise SafetyViolation("position must be a non-empty joint-to-value object")

        unknown = sorted(set(value) - set(JOINT_NAMES))
        if unknown:
            raise SafetyViolation(f"unknown joints: {', '.join(unknown)}")

        proposed = dict(self.state.positions)
        for joint, raw_position in value.items():
            try:
                position = float(raw_position)
            except (TypeError, ValueError) as exc:
                raise SafetyViolation(f"{joint} position must be numeric") from exc

            if not (
                self.safety.normalized_position_min
                <= position
                <= self.safety.normalized_position_max
            ):
                raise SafetyViolation(
                    f"{joint}={position} is outside normalized range "
                    f"[{self.safety.normalized_position_min}, "
                    f"{self.safety.normalized_position_max}]"
                )

            delta = abs(position - self.state.positions[joint])
            if delta > self.safety.max_delta_per_command + 1e-9:
                raise SafetyViolation(
                    f"{joint} delta {delta:.3f} exceeds per-command limit "
                    f"{self.safety.max_delta_per_command:.3f}"
                )
            proposed[joint] = position

        result = {
            "device_id": self.descriptor.device_id,
            "slot": "position",
            "applied": False,
            "proposed": proposed,
        }
        if not apply:
            return result
        if self.state.emergency_stop:
            raise SafetyViolation("motion blocked: emergency stop is latched")
        if self.safety.require_explicit_enable and not self.state.enabled:
            raise SafetyViolation("motion blocked: actuators are disabled")
        if self.safety.require_confirmation_for_motion and not confirmed:
            raise SafetyViolation("motion blocked: confirmed=true is required")

        self.state.positions = proposed
        self.state.sequence += 1
        result["applied"] = True
        result["sequence"] = self.state.sequence
        return result

    def _write_enabled(
        self,
        value: Any,
        *,
        apply: bool,
        confirmed: bool,
    ) -> dict[str, Any]:
        if not isinstance(value, bool):
            raise SafetyViolation("enabled must be a boolean")
        if value and self.state.emergency_stop:
            raise SafetyViolation("cannot enable while emergency stop is latched")
        if value and not confirmed:
            raise SafetyViolation("enabling actuators requires confirmed=true")

        result = {
            "device_id": self.descriptor.device_id,
            "slot": "enabled",
            "applied": False,
            "proposed": value,
        }
        if apply:
            self.state.enabled = value
            self.state.sequence += 1
            result["applied"] = True
            result["sequence"] = self.state.sequence
        return result

    def _write_emergency_stop(
        self,
        value: Any,
        *,
        apply: bool,
        confirmed: bool,
    ) -> dict[str, Any]:
        if not isinstance(value, bool):
            raise SafetyViolation("emergency_stop must be a boolean")
        if not value and not confirmed:
            raise SafetyViolation("clearing emergency stop requires confirmed=true")

        result = {
            "device_id": self.descriptor.device_id,
            "slot": "emergency_stop",
            "applied": False,
            "proposed": value,
        }
        if apply:
            self.state.emergency_stop = value
            if value:
                self.state.enabled = False
            self.state.sequence += 1
            result["applied"] = True
            result["sequence"] = self.state.sequence
        return result

    def set_object_held(self, held: bool) -> None:
        self.state.object_held = held
        self.state.sequence += 1


class Lab:
    def __init__(self, devices: Iterable[SimulatedArmDriver]):
        self.devices = {device.descriptor.device_id: device for device in devices}
        if not self.devices:
            raise ValueError("At least one device is required")

    def get(self, device_id: str) -> SimulatedArmDriver:
        try:
            return self.devices[device_id]
        except KeyError as exc:
            available = ", ".join(sorted(self.devices))
            raise KeyError(f"Unknown device {device_id!r}; available: {available}") from exc

    def discover(self) -> list[dict[str, Any]]:
        return [self.devices[key].discover() for key in sorted(self.devices)]

    def handoff_plan(self, from_device: str, to_device: str) -> dict[str, Any]:
        if from_device == to_device:
            raise SafetyViolation("handoff requires two different devices")
        source = self.get(from_device)
        target = self.get(to_device)
        step = min(source.safety.max_delta_per_command, target.safety.max_delta_per_command)
        return {
            "name": "two-arm object handoff",
            "mode": "dry-run only",
            "devices": [from_device, to_device],
            "steps": [
                {"device": from_device, "action": "move", "position": {"shoulder_pan": step}},
                {"device": from_device, "action": "close_gripper", "position": {"gripper": step}},
                {"device": to_device, "action": "move", "position": {"shoulder_pan": -step}},
                {"device": to_device, "action": "close_gripper", "position": {"gripper": step}},
                {"device": from_device, "action": "open_gripper", "position": {"gripper": 0.0}},
                {"device": from_device, "action": "return_home", "position": {"shoulder_pan": 0.0}},
                {"device": to_device, "action": "return_home", "position": {"shoulder_pan": 0.0}},
            ],
            "note": "This validates orchestration only; real handoff poses require calibration and collision checking.",
        }


def load_lab(config_path: str | Path | None = None) -> Lab:
    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "config" / "devices.example.json"
    path = Path(config_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    safety = SafetyPolicy(**raw.get("safety", {}))
    devices = []
    for item in raw["devices"]:
        descriptor = DeviceDescriptor(
            **{
                **item,
                "natural_language_tags": tuple(item.get("natural_language_tags", ())),
            }
        )
        devices.append(SimulatedArmDriver(descriptor, safety))
    return Lab(devices)
