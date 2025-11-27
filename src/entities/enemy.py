from src.config import *
from src.entities.base import Entity


class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_SIZE[0], ENEMY_SIZE[1], image_path=ENEMY_IMAGE)
        self._speed = ENEMY_SPEED

    def update(self):
        self._y += self._speed

        if self._y > SCREEN_HEIGHT:
            self.destroy()
