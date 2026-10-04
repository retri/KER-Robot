# Interface and Simulation Design

## Node boundary

| Node | Responsibility | Must not do |
|---|---|---|
| `dialog_orchestrator` | approved intent and expression request | direct actuator command |
| `perception_fusion` | timestamped person/emotion/event state | safety decision |
| `expression_planner` | face/voice/gesture target generation | bypass motion safety |
| `motion_safety_gate` | limit, timeout, e-stop and mode gate | generate conversational intent |
| `hardware_bridge` | driver protocol and feedback normalization | accept unvalidated command |
| `system_supervisor` | lifecycle, heartbeat and degraded mode | hide faults |

## Frames

`map -> odom -> base_link -> torso_link -> neck_link -> head_link`

Stage 1 desk robot uses `base_link` as the fixed product reference. `map` and `odom` remain optional until Stage 2 mobility integration. Joint frame names must match URDF; axis direction follows REP-103.

## Timing and ownership

- Safety state and e-stop: transient-local reliable, event driven.
- Joint command: reliable, deadline 40 ms draft, single publisher `motion_safety_gate`.
- Joint feedback: best-effort or reliable after driver measurement, target 50 Hz draft.
- Expression request: reliable, 10 Hz maximum unless an approved animation stream is used.
- Heartbeat: reliable, 2 Hz; missing 3 consecutive periods requests degraded/stop state.
- Every command carries `stamp`, `source`, `sequence`, `expires_at`, and `correlation_id`.

Numbers are design targets, not measured performance.

## Safety state

`INIT -> STANDBY -> ACTIVE -> DEGRADED -> SAFE_STOP`

Only `motion_safety_gate` may publish accepted actuator targets. Expired, unordered, unauthenticated or limit-violating commands are rejected. SAFE_STOP requires a separate reset condition and must not clear solely because heartbeat resumes.

## Simulation cases

| ID | Case | Expected evidence |
|---|---|---|
| SIM-01 | normal expression sequence | timing and topic trace |
| SIM-02 | command expires before execution | rejection reason |
| SIM-03 | missing hardware heartbeat | DEGRADED then SAFE_STOP |
| SIM-04 | joint target outside provisional limit | clamped or rejected by policy |
| SIM-05 | duplicated sequence | idempotent rejection |
| SIM-06 | time jump/restart | stale data not executed |
| SIM-07 | e-stop during motion | stop command and latched state |
| SIM-08 | hardware feedback delay | diagnostic and safe transition |

Real joint limits, stopping distance, torque and thermal thresholds remain TBD until F2090/F2091 and hardware safety review.
