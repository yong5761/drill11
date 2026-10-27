from pico2d import *

from boy import Boy
from grass import Grass

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


def handle_events():
    global running

    for event in get_events():
        if event.type == SDL_QUIT or (event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE):
            running = False
        else:
            for o in world:
                if hasattr(o, 'handle_event'):
                    o.handle_event(event)


def reset_world():
    global world

    world = []
    world.append(Grass())
    world.append(Boy())


def update_world():
    for o in world:
        o.update()


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()
