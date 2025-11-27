# src/entities/bullet.py
from src.config import *
from src.entities.base import Entity


class Bullet(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, BULLET_SIZE[0], BULLET_SIZE[1], image_path=BULLET_IMAGE)
        self._speed = BULLET_SPEED

    def update(self):
        self._y -= self._speed

        if self._y < 0:
            self.destroy()
