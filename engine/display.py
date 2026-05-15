"""
Display abstraction.

On the Pi no environment variables are required.  The class picks a
driver automatically:

  /dev/fb1 exists  →  fbcon on /dev/fb1  (ST7789 SPI TFT — preferred)
  /dev/fb1 absent  →  kmsdrm             (HDMI via DRM/KMS)
  both fail        →  offscreen          (headless / SSH fallback)

To force a specific driver:
    SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb1 python main.py

On Mac/dev the config SCALE > 1 so you get a scaled-up window instead.
"""

import os
import sys
import pygame
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS


def _init_linux_display() -> str:
    """Choose and initialise the best SDL video driver; return its name."""
    os.environ.setdefault("SDL_NOMOUSE", "1")

    # Respect an explicit override from the environment.
    if "SDL_VIDEODRIVER" in os.environ:
        pygame.display.init()
        return os.environ["SDL_VIDEODRIVER"]

    # If the SPI framebuffer device exists, use it directly via fbcon.
    # This is the correct path for the ST7789 TFT.
    if os.path.exists("/dev/fb1"):
        os.environ["SDL_VIDEODRIVER"] = "fbcon"
        os.environ["SDL_FBDEV"]       = "/dev/fb1"
        drivers = ["fbcon", "offscreen"]
    else:
        # No SPI display yet — fall back to kmsdrm (HDMI) then offscreen.
        drivers = ["kmsdrm", "offscreen"]

    for driver in drivers:
        os.environ["SDL_VIDEODRIVER"] = driver
        try:
            pygame.display.init()
            print(f"display: SDL_VIDEODRIVER={driver}"
                  + (f" SDL_FBDEV={os.environ['SDL_FBDEV']}"
                     if driver == "fbcon" else ""))
            return driver
        except pygame.error:
            pygame.display.quit()

    raise SystemExit(
        "No usable SDL video driver found.\n"
        "After wiring the ST7789, reboot and check that /dev/fb1 exists.\n"
        "On Pi: ensure you are in the 'video' group:\n"
        "  sudo usermod -aG video $USER  (then log out and back in)"
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
