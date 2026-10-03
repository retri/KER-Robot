from dataclasses import dataclass, field
from typing import Dict, Mapping
from .contracts import GateResult, JointCommand

ACTIVE = "ACTIVE"
SAFE_STOP = "SAFE_STOP"

@dataclass
class SafetyGate:
    limits: Mapping[str, tuple[float, float]]
    state: str = SAFE_STOP
    last_sequence: Dict[str, int] = field(default_factory=dict)

    def set_state(self, state: str) -> None:
        if state not in {"INIT", "STANDBY", "ACTIVE", "DEGRADED", "SAFE_STOP"}:
            raise ValueError("unknown safety state")
        self.state = state

    def evaluate(self, command: JointCommand, now: float) -> GateResult:
        if self.state != ACTIVE:
            return GateResult(False, f"state:{self.state}", {})
        if not command.source or not command.correlation_id:
            return GateResult(False, "missing_trace_identity", {})
        if command.expires_at <= now or command.stamp > now + 0.25:
            return GateResult(False, "stale_or_future_command", {})
        previous = self.last_sequence.get(command.source, -1)
        if command.sequence <= previous:
            return GateResult(False, "duplicate_or_out_of_order", {})
        if set(command.positions) - set(self.limits):
            return GateResult(False, "unknown_joint", {})
        for joint, value in command.positions.items():
            low, high = self.limits[joint]
            if not low <= value <= high:
                return GateResult(False, f"limit:{joint}", {})
        self.last_sequence[command.source] = command.sequence
        return GateResult(True, "accepted", dict(command.positions))
