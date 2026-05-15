from abc import ABC, abstractmethod
import pygame
from engine.input import InputState


class Screen(ABC):
    """Base class for all screens. Returns the next Screen to show, or None to quit."""

    @abstractmethod
    def update(self, state: InputState) -> "Screen | None":
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        ...
