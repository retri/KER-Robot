from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class JointCommand:
    stamp: float
    source: str
    sequence: int
    expires_at: float
    correlation_id: str
    positions: Mapping[str, float]

@dataclass(frozen=True)
class GateResult:
    accepted: bool
    reason: str
    positions: Mapping[str, float]
