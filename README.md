# Drill #11 — 소년 자동 무적 런(AutoRun) 상태 추가

2D 게임 프로그래밍 Drill #11 과제. `transitions` 상태 머신으로 동작하는
소년 캐릭터 컨트롤러에 **자동 무적 런(AUTO_RUN)** 상태를 추가했다.

개발 기획·요구사항은 [PRD.md](PRD.md) 참고.

---

## 실행

```bash
pip install pico2d transitions
python main.py
```

상태 머신 로직만 빠르게 검증하려면 (캔버스 없이 실행):

```bash
python test_state_machine.py
```

상태 다이어그램 이미지를 다시 생성하려면:

```bash
python make_diagram.py
```

---

## 조작법

| 키 | 동작 |
|----|------|
| `→` / `←` | 해당 방향으로 달리기 |
| `a` | 자동 무적 런 시작 |
| `SPACE` | 취침 상태에서 깨어나기 |
| `ESC` | 종료 |

---

## 상태 다이어그램

![상태 다이어그램](state_diagram.png)

---

## 구현 요약

### AUTO_RUN 상태

| 항목 | 값 |
|------|-----|
| 진입 | `IDLE`에서 `a` 키 |
| 이동 속도 | 평소 달리기의 3배 (5 → 15 px/frame) |
| 캐릭터 크기 | 1.6배 (100 → 160 px) |
| 화면 끝 | 좌우 경계에서 진행 방향 자동 반전 |
| 자동 종료 | 진입 후 5초 경과 시 `IDLE` 복귀 |
| 수동 취소 | 방향키를 누르면 그 방향의 `RUN`으로 전환 |

### 상태 클래스 구조

각 상태는 `transitions.State`를 상속하여 자신의 진입/이탈 동작과
매 프레임 동작, 렌더링을 직접 책임진다.

```
transitions.State
└── BoyState            enter/exit 훅을 start/finish 로 위임
    ├── IdleState       프레임 갱신 + 5초 타이머 → SLEEP
    ├── SleepState      90도 회전하여 눕는 렌더링
    ├── RunState        좌우 이동 + 화면 경계 제한
    └── AutoRunState    고속 이동 + 자동 방향 반전 + 5초 타이머 → IDLE
```

`Boy`는 상태 객체를 직접 보관하지 않고,
`self.machine.get_state(self.state)`로 현재 상태를 조회해 동작을 위임한다.

### 버그 수정

취침 중 방향키를 눌러도 반응이 없어 `SPACE`를 누르기 전까지 `SLEEP`에
갇히던 문제를 수정했다. `go_to_run` 트랜지션의 source가 `IDLE` 하나뿐이라
`SLEEP`에서는 트리거가 무시되고 있었다.

---

## 파일 구성

| 파일 | 설명 |
|------|------|
| `main.py` | 게임 루프, 이벤트 분배, 월드 관리 |
| `boy.py` | Boy 캐릭터 및 상태 머신 조립 |
| `state.py` | 상태 클래스 (`BoyState` 및 4개 구체 상태) |
| `grass.py` | 배경 잔디 오브젝트 |
| `test_state_machine.py` | 상태 전이 검증 스크립트 |
| `make_diagram.py` | 상태 다이어그램 이미지 생성 스크립트 |
| `PRD.md` | 개발 기획·요구사항 문서 |
| `state_diagram.png` | 상태 다이어그램 (제출물) |
