# F2030-S01 ROS 2 Node / Topic Architecture

Jira: [KR1-248](https://lumira077.atlassian.net/browse/KR1-248)

Stage 1 KER Lumira의 대화·인지·표현·구동 모듈을 연결하기 위한 ROS 2 인터페이스 기준 초안이다. 실제 모터 토크·속도·가동범위는 하드웨어 사양과 안전시험 승인 전까지 확정값으로 사용하지 않는다.

## 산출물

- `docs/interface.md`: node, topic, frame, QoS, timing, fail-safe 설계
- `config/topic_contract.json`: 기계 판독 가능한 topic 계약
- `scripts/validate_contract.py`: 계약 정적 검증
- `tests/test_contract.py`: 표준 라이브러리 기반 검증 시험

## 검토 Gate

1. R3: node/topic 명명과 control ownership
2. R4: MCU/driver 연결 주기, watchdog, timestamp
3. R6/Q1: 축 한계, 충돌·끼임·전도 위험과 시험 조건
4. R1: Stage 1 범위와 F2031~F2036 연결

현재 결과는 설계·Simulation 준비 단계이며 실물 로봇 안전 통과를 의미하지 않는다.
