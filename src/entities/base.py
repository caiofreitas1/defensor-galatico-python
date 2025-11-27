# src/entities/base.py
import pygame
from abc import ABC, abstractmethod


class Entity(ABC):
    """
    Classe base abstrata para todos os objetos do jogo.
    Demonstra: Classes Abstratas e Encapsulamento.
    """
    def __init__(self, x, y, width, height, image_path=None):
        # Encapsulamento: Atributos protegidos com _
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._is_active = True

        if image_path:
            self._image = pygame.image.load(image_path).convert_alpha()
            self._image = pygame.transform.scale(self._image, (width, height))
        else:
            self._image = None
        
        self._rect = pygame.Rect(x, y, width, height)

    @property
    def rect(self):
        """Getter para o retângulo de colisão (Encapsulamento)."""
        # Atualiza a posição do rect antes de retorná-lo
        self._rect.topleft = (self._x, self._y)
        return self._rect

    @property
    def is_active(self):
        return self._is_active

    def destroy(self):
        self._is_active = False

    @abstractmethod
    def update(self):
        pass

    def draw(self, surface):
        if self._image:
            surface.blit(self._image, (self._x, self._y))
        else:
            pygame.draw.rect(surface, (255, 255, 255), self.rect)