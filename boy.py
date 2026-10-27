from pico2d import (SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a, SDL_KEYDOWN,
                    SDL_KEYUP, get_time, load_image)
from transitions import Machine

from state import AutoRunState, IdleState, RunState, SleepState

ARROW_KEYS = (SDLK_LEFT, SDLK_RIGHT)

# 방향키를 눌러 달리기를 시작할 수 있는 상태들.
# SLEEP 이 빠져 있으면 취침 후 SPACE 를 누르기 전까지 영영 깨어나지 못한다.
RUNNABLE_FROM = ['IDLE', 'SLEEP']


class Boy:
    """소년 캐릭터. 상태 머신을 조립하고, 동작은 각 상태 객체에 위임한다."""

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1  # 1=오른쪽, -1=왼쪽
        self.idle_start = get_time()
        self.auto_run_start = 0.0
        self.image = load_image('animation_sheet.png')

        self.machine = Machine(
            model=self,
            states=[IdleState(), SleepState(), RunState(), AutoRunState()],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('go_to_sleep', 'IDLE', 'SLEEP')
        # IDLE 진입 시 Entry action 이 5초 타이머를 다시 시작한다.
        self.machine.add_transition('go_to_idle', ['SLEEP', 'RUN', 'AUTO_RUN'], 'IDLE')
        self.machine.add_transition('go_to_run', RUNNABLE_FROM, 'RUN')
        self.machine.add_transition('go_to_auto_run', 'IDLE', 'AUTO_RUN')

    @property
    def current_state(self):
        """현재 상태에 대응하는 상태 객체."""
        return self.machine.get_state(self.state)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            self._on_key_down(event.key)
        elif event.type == SDL_KEYUP:
            self._on_key_up(event.key)

    def _on_key_down(self, key):
        if key == SDLK_SPACE and self.state == 'SLEEP':
            self.go_to_idle()
        elif key in ARROW_KEYS and self.state in RUNNABLE_FROM:
            self.face_dir = 1 if key == SDLK_RIGHT else -1
            self.go_to_run()
        elif key == SDLK_a and self.state == 'IDLE':
            self.go_to_auto_run()

    def _on_key_up(self, key):
        if key in ARROW_KEYS and self.state == 'RUN':
            self.go_to_idle()

    def update(self):
        self.current_state.do(self)

    def draw(self):
        self.current_state.draw(self)
