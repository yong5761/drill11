"""소년 캐릭터의 상태 클래스 모음.

각 상태는 transitions.State 를 상속하여, 자신의 진입/이탈 동작과
매 프레임 동작(do), 렌더링(draw)을 스스로 책임진다.
"""

from pico2d import get_time
from transitions import State

# 스프라이트 시트 규격 (animation_sheet.png, 100x100px · 8프레임 × 4행)
FRAME_WIDTH = 100
FRAME_HEIGHT = 100
FRAME_COUNT = 8

# pico2d 는 y축이 아래에서 위로 증가하므로, 시트의 맨 윗줄이 y=300 이다.
ROW_IDLE_RIGHT = 300
ROW_IDLE_LEFT = 200
ROW_RUN_RIGHT = 100
ROW_RUN_LEFT = 0

CANVAS_WIDTH = 800

# 캐릭터가 달릴 수 있는 좌우 경계
LEFT_BOUNDARY = 50
RIGHT_BOUNDARY = 750

IDLE_TIMEOUT = 5.0  # IDLE 상태로 이만큼 지나면 SLEEP


class BoyState(State):
    """상태 베이스.

    transitions 가 호출하는 enter/exit 훅을 받아, 모델(Boy)을 인자로 넘기는
    start/finish 로 위임한다. 하위 상태는 start/finish/do/draw 만 구현하면 된다.
    """

    def enter(self, event_data):
        super().enter(event_data)
        self.start(event_data.model)

    def exit(self, event_data):
        super().exit(event_data)
        self.finish(event_data.model)

    def start(self, boy):
        """상태 진입 시 1회 수행 (Entry action)."""

    def finish(self, boy):
        """상태 이탈 시 1회 수행 (Exit action)."""

    def do(self, boy):
        """상태에 머무는 동안 매 프레임 수행 (Do activity)."""

    def draw(self, boy):
        """현재 상태의 캐릭터를 화면에 그린다."""
        raise NotImplementedError


class IdleState(BoyState):
    """제자리에서 바라보는 방향으로 대기한다. 5초가 지나면 취침한다."""

    def __init__(self):
        super().__init__(name='IDLE')

    def start(self, boy):
        boy.frame = 0
        boy.idle_start = get_time()

    def do(self, boy):
        boy.frame = (boy.frame + 1) % FRAME_COUNT
        if get_time() - boy.idle_start > IDLE_TIMEOUT:
            boy.go_to_sleep()

    def draw(self, boy):
        row = ROW_IDLE_RIGHT if boy.face_dir == 1 else ROW_IDLE_LEFT
        boy.image.clip_draw(boy.frame * FRAME_WIDTH, row,
                            FRAME_WIDTH, FRAME_HEIGHT, boy.x, boy.y)


class SleepState(BoyState):
    """취침. 바라보던 방향으로 90도 누운 채 정지한다."""

    # 누웠을 때 몸이 지면에 닿도록 중심을 내리는 보정값
    LYING_OFFSET = 25

    def __init__(self):
        super().__init__(name='SLEEP')

    def start(self, boy):
        boy.frame = 0

    def draw(self, boy):
        if boy.face_dir == 1:
            row, angle = ROW_IDLE_RIGHT, -90
        else:
            row, angle = ROW_IDLE_LEFT, 90
        boy.image.clip_composite_draw(
            0, row, FRAME_WIDTH, FRAME_HEIGHT,
            angle, '', boy.x, boy.y - self.LYING_OFFSET,
            FRAME_WIDTH, FRAME_HEIGHT,
        )


class RunState(BoyState):
    """방향키를 누르고 있는 동안 해당 방향으로 달린다."""

    SPEED = 5

    def __init__(self):
        super().__init__(name='RUN')

    def start(self, boy):
        boy.frame = 0

    def do(self, boy):
        boy.frame = (boy.frame + 1) % FRAME_COUNT
        boy.x += self.SPEED * boy.face_dir
        # 캔버스 좌우 가장자리를 넘어가지 않는다.
        boy.x = max(LEFT_BOUNDARY, min(RIGHT_BOUNDARY, boy.x))

    def draw(self, boy):
        row = ROW_RUN_RIGHT if boy.face_dir == 1 else ROW_RUN_LEFT
        boy.image.clip_draw(boy.frame * FRAME_WIDTH, row,
                            FRAME_WIDTH, FRAME_HEIGHT, boy.x, boy.y)


class AutoRunState(BoyState):
    """자동 무적 런.

    키 조작 없이 스스로 좌우로 계속 이동한다.
    """

    SPEED = RunState.SPEED * 3          # 평소 달리기의 3배 속도
    SIZE = int(FRAME_WIDTH * 1.6)       # 1.6배로 확대된 캐릭터 크기
    DURATION = 5.0                      # 이만큼 지나면 스스로 IDLE 로 돌아간다

    # 확대해도 발이 같은 지면에 닿도록 중심을 올려주는 보정값
    GROUND_OFFSET = (SIZE - FRAME_HEIGHT) // 2

    # 확대된 몸이 화면 밖으로 삐져나가지 않는 반전 지점
    LEFT_LIMIT = SIZE // 2
    RIGHT_LIMIT = CANVAS_WIDTH - SIZE // 2

    def __init__(self):
        super().__init__(name='AUTO_RUN')

    def start(self, boy):
        boy.frame = 0
        boy.auto_run_start = get_time()

    def do(self, boy):
        boy.frame = (boy.frame + 1) % FRAME_COUNT
        boy.x += self.SPEED * boy.face_dir
        self._turn_at_edge(boy)

        if get_time() - boy.auto_run_start > self.DURATION:
            boy.go_to_idle()

    def _turn_at_edge(self, boy):
        """화면 좌우 끝에 닿으면 진행 방향을 반대로 뒤집는다."""
        if boy.x <= self.LEFT_LIMIT:
            boy.x = self.LEFT_LIMIT
            boy.face_dir = 1
        elif boy.x >= self.RIGHT_LIMIT:
            boy.x = self.RIGHT_LIMIT
            boy.face_dir = -1

    def draw(self, boy):
        row = ROW_RUN_RIGHT if boy.face_dir == 1 else ROW_RUN_LEFT
        boy.image.clip_composite_draw(
            boy.frame * FRAME_WIDTH, row, FRAME_WIDTH, FRAME_HEIGHT,
            0, '', boy.x, boy.y + self.GROUND_OFFSET,
            self.SIZE, self.SIZE,
        )
