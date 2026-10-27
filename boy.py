from pico2d import SDLK_SPACE, SDL_KEYDOWN, get_time, load_image
from transitions import Machine

from state import IdleState, SleepState


class Boy:
    """소년 캐릭터. 상태 머신을 조립하고, 동작은 각 상태 객체에 위임한다."""

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1  # 1=오른쪽, -1=왼쪽
        self.idle_start = get_time()
        self.image = load_image('animation_sheet.png')

        self.machine = Machine(
            model=self,
            states=[IdleState(), SleepState()],
            initial='IDLE',
            auto_transitions=False,
        )
        self.machine.add_transition('go_to_sleep', 'IDLE', 'SLEEP')
        # IDLE 진입 시 Entry action 이 5초 타이머를 다시 시작한다.
        self.machine.add_transition('go_to_idle', 'SLEEP', 'IDLE')

    @property
    def current_state(self):
        """현재 상태에 대응하는 상태 객체."""
        return self.machine.get_state(self.state)

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN:
            return

        if event.key == SDLK_SPACE and self.state == 'SLEEP':
            self.go_to_idle()

    def update(self):
        self.current_state.do(self)

    def draw(self):
        self.current_state.draw(self)
