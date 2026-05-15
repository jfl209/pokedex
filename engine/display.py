"""
Display abstraction.

On the Pi no environment variables are required — the class probes SDL
drivers automatically in preference order (kmsdrm → fbcon → offscreen).

To force a specific driver:
    SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb1 python main.py

On Mac/dev the config SCALE > 1 so you get a scaled-up window instead.
"""

import os
import sys
import pygame
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS

# Tried in order on Linux when SDL_VIDEODRIVER is not already set.
# kmsdrm  — default on Raspberry Pi OS Bullseye+ (no X11 needed)
# fbcon   — older Pi OS / custom kernels; needs /dev/fb0 or /dev/fb1
# offscreen — silent fallback so the app at least starts for debugging
_LINUX_DRIVERS = ["kmsdrm", "fbcon", "offscreen"]


def _init_linux_display() -> str:
    """Probe SDL video drivers in order; return the one that worked."""
    os.environ.setdefault("SDL_NOMOUSE", "1")

    # If the caller already chose a driver, honour it and fail loudly.
    if "SDL_VIDEODRIVER" in os.environ:
        pygame.display.init()
        return os.environ["SDL_VIDEODRIVER"]

    for driver in _LINUX_DRIVERS:
        os.environ["SDL_VIDEODRIVER"] = driver

        # fbcon needs to know which framebuffer device to use.
        if driver == "fbcon":
            # Prefer /dev/fb1 (SPI display) but fall back to /dev/fb0.
            for fb in ("/dev/fb1", "/dev/fb0"):
                if os.path.exists(fb):
                    os.environ.setdefault("SDL_FBDEV", fb)
                    break

        try:
            pygame.display.init()
            print(f"display: SDL_VIDEODRIVER={driver}")
            return driver
        except pygame.error:
            pygame.display.quit()

    raise SystemExit(
        "No usable SDL video driver found.\n"
        "On Pi: ensure the display overlay is loaded and you are in the 'video' group.\n"
        "Try:  sudo usermod -aG video $USER  then log out and back in."
    )


class Display:
    def __init__(self) -> None:
        if sys.platform == "linux":
            driver = _init_linux_display()
            self._fullscreen = (SCALE == 1 and driver != "offscreen")
        else:
            pygame.display.init()
            self._fullscreen = False

        flags = (pygame.FULLSCREEN | pygame.NOFRAME) if self._fullscreen else 0
        self._window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Pokédex")

        # Native-res surface — all drawing happens here, then scaled up.
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
