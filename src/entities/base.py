# src/entities/base.py
import pygame
from abc import ABC, abstractmethod

class Entity(ABC):
    """
    Classe base abstrata para todos os objetos do jogo.
    Demonstra: Classes Abstratas e Encapsulamento.
    """
    def __init__(self, x, y, width, height, color):
        # Encapsulamento: Atributos protegidos com _
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._color = color
        self._rect = pygame.Rect(x, y, width, height)
        self._is_active = True

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
        """
        Método abstrato. Obriga as classes filhas a implementarem
        seu próprio comportamento de movimento.
        """
        pass

    def draw(self, surface):
        """Desenha o objeto na tela."""
        pygame.draw.rect(surface, self._color, self.rect)