"""상태 머신 로직 검증 스크립트.

캔버스를 열지 않고 상태 전이만 확인하기 위해, 이미지 로딩과 시간 함수를
가짜로 대체한 뒤 PRD 8장의 검증 시나리오를 그대로 따라간다.

실행: python test_state_machine.py
"""

from pico2d import SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a, SDL_KEYDOWN, SDL_KEYUP

import boy as boy_module
import state as state_module


class FakeImage:
    """그리기 호출을 전부 삼키는 더미 이미지."""

    def clip_draw(self, *args):
        pass

    def clip_composite_draw(self, *args):
        pass


class FakeEvent:
    def __init__(self, type_, key=None):
        self.type = type_
        self.key = key


clock = {'now': 0.0}


def fake_get_time():
    return clock['now']


def advance(seconds):
    clock['now'] += seconds


# pico2d 의존성 제거
state_module.get_time = fake_get_time
boy_module.get_time = fake_get_time
boy_module.load_image = lambda _name: FakeImage()

Boy = boy_module.Boy
AutoRunState = state_module.AutoRunState

PASSED = []
FAILED = []


def check(label, actual, expected):
    if actual == expected:
        PASSED.append(label)
        print(f'  [PASS] {label}: {actual}')
    else:
        FAILED.append(label)
        print(f'  [FAIL] {label}: expected {expected}, got {actual}')


def press(boy, key):
    boy.handle_event(FakeEvent(SDL_KEYDOWN, key))


def release(boy, key):
    boy.handle_event(FakeEvent(SDL_KEYUP, key))


def new_boy():
    clock['now'] = 0.0
    return Boy()


def scenario_1_idle_to_sleep():
    print('시나리오 1 — 5초 대기 시 SLEEP 전환')
    boy = new_boy()
    check('초기 상태', boy.state, 'IDLE')
    advance(6)
    boy.update()
    check('5초 경과 후', boy.state, 'SLEEP')


def scenario_2_sleep_to_idle_with_space():
    print('시나리오 2 — SLEEP 에서 SPACE 로 기상')
    boy = new_boy()
    advance(6)
    boy.update()
    press(boy, SDLK_SPACE)
    check('SPACE 입력 후', boy.state, 'IDLE')

    # IDLE 진입 Entry action 이 타이머를 다시 시작했는지 확인
    advance(3)
    boy.update()
    check('3초만 지났을 때', boy.state, 'IDLE')
    advance(3)
    boy.update()
    check('다시 5초 넘겼을 때', boy.state, 'SLEEP')


def scenario_3_sleep_to_run_with_arrow():
    print('시나리오 3 — SLEEP 에서 방향키로 탈출 (버그 수정 확인)')
    boy = new_boy()
    advance(6)
    boy.update()
    check('취침 확인', boy.state, 'SLEEP')
    press(boy, SDLK_LEFT)
    check('좌측 방향키 입력 후', boy.state, 'RUN')
    check('바라보는 방향', boy.face_dir, -1)


def scenario_4_idle_to_auto_run():
    print("시나리오 4 — IDLE 에서 'a' 키로 AUTO_RUN 진입")
    boy = new_boy()
    press(boy, SDLK_a)
    check("'a' 입력 후", boy.state, 'AUTO_RUN')
    check('속도가 RUN 의 3배', AutoRunState.SPEED, state_module.RunState.SPEED * 3)
    check('크기가 확대됨', AutoRunState.SIZE > state_module.FRAME_WIDTH, True)


def scenario_5_auto_run_bounces():
    print('시나리오 5 — AUTO_RUN 이 화면 끝에서 방향 전환')
    boy = new_boy()
    press(boy, SDLK_a)
    boy.face_dir = 1

    # 오른쪽 끝까지 달린다 (5초 타임아웃 전에 도달하도록 시간은 멈춰둔다)
    for _ in range(200):
        boy.update()
        if boy.face_dir == -1:
            break
    check('우측 끝에서 좌향 반전', boy.face_dir, -1)
    check('우측 한계 안쪽', boy.x <= AutoRunState.RIGHT_LIMIT, True)

    for _ in range(200):
        boy.update()
        if boy.face_dir == 1:
            break
    check('좌측 끝에서 우향 반전', boy.face_dir, 1)
    check('좌측 한계 바깥쪽', boy.x >= AutoRunState.LEFT_LIMIT, True)


def scenario_6_auto_run_timeout():
    print('시나리오 6 — AUTO_RUN 5초 경과 시 IDLE 복귀')
    boy = new_boy()
    press(boy, SDLK_a)
    advance(6)
    boy.update()
    check('5초 경과 후', boy.state, 'IDLE')


def scenario_7_auto_run_cancel_with_arrow():
    print('시나리오 7 — AUTO_RUN 중 방향키로 무적 런 취소')
    boy = new_boy()
    press(boy, SDLK_a)
    check('무적 런 진입', boy.state, 'AUTO_RUN')
    press(boy, SDLK_RIGHT)
    check('우측 방향키 입력 후', boy.state, 'RUN')
    check('바라보는 방향', boy.face_dir, 1)
    release(boy, SDLK_RIGHT)
    check('방향키를 뗀 뒤', boy.state, 'IDLE')


def main():
    for scenario in (
        scenario_1_idle_to_sleep,
        scenario_2_sleep_to_idle_with_space,
        scenario_3_sleep_to_run_with_arrow,
        scenario_4_idle_to_auto_run,
        scenario_5_auto_run_bounces,
        scenario_6_auto_run_timeout,
        scenario_7_auto_run_cancel_with_arrow,
    ):
        scenario()
        print()

    print(f'통과 {len(PASSED)}건, 실패 {len(FAILED)}건')
    if FAILED:
        for label in FAILED:
            print(f'  - {label}')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
