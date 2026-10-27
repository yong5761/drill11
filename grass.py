from pico2d import load_image


class Grass:
    """배경 잔디 오브젝트."""

    def __init__(self):
        self.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)
