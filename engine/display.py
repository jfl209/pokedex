"""
Display abstraction.

On the Pi, drives the ST7789 directly over SPI — no dtoverlay or
framebuffer driver required. pygame renders to an offscreen surface;
each flip() converts pixels to RGB565 and pushes them via spidev.

On Mac/dev, SCALE > 1 opens a scaled-up window for comfortable editing.

To force kmsdrm (HDMI output for debugging):
    SDL_VIDEODRIVER=kmsdrm python main.py
"""

import os
import sys
import pygame
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS


def _try_st7789():
    """Return an initialised ST7789 instance, or None if not on Pi / no spidev."""
    try:
        import spidev as _spidev   # noqa: F401 — just checking availability
        import RPi.GPIO as _gpio   # noqa: F401
        import numpy as _np        # noqa: F401
        from engine.st7789 import ST7789
        return ST7789()
    except Exception as e:
        print(f"display: ST7789 not available ({e})")
        return None


def _init_sdl_linux() -> str:
    """Probe SDL drivers on Linux; return the one that worked."""
    os.environ.setdefault("SDL_NOMOUSE", "1")
    if "SDL_VIDEODRIVER" in os.environ:
        pygame.display.init()
        return os.environ["SDL_VIDEODRIVER"]
    for driver in ("kmsdrm", "offscreen"):
        os.environ["SDL_VIDEODRIVER"] = driver
        try:
            pygame.display.init()
            print(f"display: SDL_VIDEODRIVER={driver}")
            return driver
        except pygame.error:
            pygame.display.quit()
    raise SystemExit("No usable SDL video driver found.")


class Display:
    def __init__(self) -> None:
        self._tft = None

        if sys.platform == "linux":
            self._tft = _try_st7789()

        if self._tft:
            # No pygame display window needed — we write pixels directly to the
            # TFT over SPI. pygame.init() was already called in main.py so
            # Surface creation and font/event subsystems work fine without a
            # display window. Avoid set_mode() entirely: it would try to create
            # a kmsdrm window (already active from pygame.init) and hang.
            self._surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        else:
            if sys.platform == "linux":
                driver = _init_sdl_linux()
                fullscreen = (SCALE == 1 and driver != "offscreen")
            else:
                pygame.display.init()
                fullscreen = False

            flags = (pygame.FULLSCREEN | pygame.NOFRAME) if fullscreen else 0
            self._window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
            pygame.display.set_caption("Pokédex")
            self._surface = (
                pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT)) if SCALE > 1
                else self._window
            )

        self._clock = pygame.time.Clock()

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    def flip(self) -> None:
        if self._tft:
            self._tft.blit_surface(self._surface)
        elif SCALE > 1:
            scaled = pygame.transform.scale(self._surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            self._window.blit(scaled, (0, 0))
            pygame.display.flip()
        else:
            pygame.display.flip()
        self._clock.tick(FPS)
