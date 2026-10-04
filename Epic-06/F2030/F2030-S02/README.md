# F2030-S02 ROS 2 / Hardware Integration Skeleton

Jira: [KR1-249](https://lumira077.atlassian.net/browse/KR1-249)

S01 topic contract를 코드에서 검사하고, 안전 Gate를 통과한 명령만 hardware bridge로 전달하기 위한 ROS 2 독립형 참조 골격이다. ROS 2 package, MCU protocol 및 실제 joint limits는 후속 Bench 작업에서 연결한다.

## Included

- `ker_ros2_bridge/contracts.py`: command/feedback data contract
- `ker_ros2_bridge/safety_gate.py`: expiry, sequence, mode, limit checks
- `tests/test_safety_gate.py`: hardware-independent tests

## Run

```bash
python -m unittest discover -s Epic-06/F2030/F2030-S02/tests -v
```

이 시험은 순수 로직 검증이다. 실제 actuator 정지거리·토크·온도·통신지연 검증은 포함하지 않는다.
