#!/usr/bin/env python3
"""
Pokédex — main entry point.

Run on Mac:
    python main.py

Run on Pi (after setting up /dev/fb0 framebuffer driver):
    POKEDEX_SCALE=1 SDL_FBDEV=/dev/fb0 SDL_VIDEODRIVER=fbcon SDL_NOMOUSE=1 python main.py
"""

import sys
import os
import pygame

from engine.display import Display
from engine.input   import poll
from screens.home   import HomeScreen
import data.db as db


def load_fonts() -> dict:
    # Uses pygame's built-in font; swap for a pixel TTF (e.g. "Press Start 2P")
    # by placing it in assets/ and passing the path to pygame.font.Font().
    return {
        "title": pygame.font.SysFont("monospace", 22, bold=True),
        "large": pygame.font.SysFont("monospace", 18, bold=True),
        "small": pygame.font.SysFont("monospace", 11),
        "tiny":  pygame.font.SysFont("monospace",  9),
    }


def main() -> None:
    if not db.is_populated():
        print("Database is empty. Run:  python -m data.fetch")
        print("Continuing with empty database — browse screen will be blank.")

    pygame.init()
    display = Display()
    fonts   = load_fonts()
    screen  = HomeScreen(fonts)

    while screen is not None:
        state  = poll()
        screen = screen.update(state)
        if screen is not None:
            screen.draw(display.surface)
            display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
