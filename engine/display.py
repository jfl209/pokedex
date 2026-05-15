"""
Display abstraction.

On the Pi, set POKEDEX_SCALE=1 (or let config.py detect linux) and the
SDL environment variables so pygame renders to /dev/fb0:

    export SDL_FBDEV=/dev/fb0
    export SDL_VIDEODRIVER=fbcon
    export SDL_NOMOUSE=1

On Mac/dev the config SCALE > 1, so you get a scaled-up window.
"""

import os
import pygame
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS


class Display:
    def __init__(self) -> None:
        pygame.display.init()

        flags = 0
        if SCALE == 1 and os.environ.get("SDL_VIDEODRIVER") == "fbcon":
            flags = pygame.FULLSCREEN | pygame.NOFRAME

        self._window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Pokédex")

        # Native-res surface — all drawing happens here, then scaled up
        if SCALE > 1:
            self._surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        else:
            self._surface = self._window

        self._clock = pygame.time.Clock()

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    def flip(self) -> None:
        if SCALE > 1:
            scaled = pygame.transform.scale(self._surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self._window.blit(scaled, (0, 0))
        pygame.display.flip()
        self._clock.tick(FPS)
