# src/entities/player.py
import pygame
from src.config import *
from src.entities.base import Entity


class Player(Entity):
    def __init__(self):
        # Inicia no centro inferior da tela
        super().__init__(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT - 60,
            width=PLAYER_SIZE[0],
            height=PLAYER_SIZE[1],
            color=GREEN
        )
        self._speed = PLAYER_SPEED

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self._x > 0:
            self._x -= self._speed
        if keys[pygame.K_RIGHT] and self._x < SCREEN_WIDTH - self._width:
            self._x += self._speed

    def move_up(self):
        pass