import math
import pygame
from screens.base import Screen
from engine.input import InputState, Button
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, BLACK, RED, WHITE

_CREAM    = (248, 242, 200)   # warm GBC paper colour
_GOLD     = (210, 168,   0)
_DARK_RED = (130,  10,  10)
_DARK     = ( 40,  32,  48)
_DIM      = (160, 130, 110)


def _t(surface, font, text, color, cx, y, bg, shadow_color=None, shadow_offset=1):
    """Centre-render text at (cx, y). bg must match the destination so blit is opaque-safe."""
    if shadow_color is not None:
        shad = font.render(text, True, shadow_color, bg)
        surface.blit(shad, shad.get_rect(centerx=cx + shadow_offset, top=y + shadow_offset))
    main = font.render(text, True, color, bg)
    rect = main.get_rect(centerx=cx, top=y)
    surface.blit(main, rect)
    return rect.bottom


def _pokeball(surface, cx, cy, r):
    pygame.draw.circle(surface, BLACK, (cx, cy), r)
    pygame.draw.circle(surface, (225, 225, 225), (cx, cy), r - 2)
    top_half = [
        (cx + (r - 2) * math.cos(math.radians(a)),
         cy + (r - 2) * math.sin(math.radians(a)))
        for a in range(181, 360)
    ]
    top_half.append((cx, cy))
    pygame.draw.polygon(surface, RED, top_half)
    pygame.draw.line(surface, BLACK, (cx - r + 2, cy), (cx + r - 2, cy), 3)
    pygame.draw.circle(surface, BLACK, (cx, cy), 11)
    pygame.draw.circle(surface, (55, 55, 55), (cx, cy), 9)
    pygame.draw.circle(surface, WHITE, (cx, cy), 6)


class HomeScreen(Screen):
    def __init__(self, fonts: dict) -> None:
        self._fonts = fonts
        self._tick  = 0

    def update(self, state: InputState) -> "Screen | None":
        self._tick += 1
        if state.quit:
            return None
        if Button.A in state.just_down or Button.START in state.just_down:
            from screens.browse import BrowseScreen
            return BrowseScreen(self._fonts)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        cx = DISPLAY_WIDTH // 2
        surface.fill(_CREAM)

        # ── Red header stripe ──────────────────────────────────────────────
        pygame.draw.rect(surface, RED,      (0,  0, DISPLAY_WIDTH, 48))
        pygame.draw.rect(surface, _GOLD,    (0, 47, DISPLAY_WIDTH,  3))

        # small corner pokeballs inside the header
        for bx in (18, DISPLAY_WIDTH - 18):
            _pokeball(surface, bx, 24, 13)

        _t(surface, self._fonts["title"], "POKÉDEX",
           WHITE, cx, 10, bg=RED,
           shadow_color=_DARK_RED, shadow_offset=2)

        # ── Cream content area ─────────────────────────────────────────────
        _t(surface, self._fonts["small"], "K A N T O   E D I T I O N",
           _DARK, cx, 58, bg=_CREAM,
           shadow_color=_DIM, shadow_offset=1)

        pygame.draw.line(surface, RED,   (28, 75), (DISPLAY_WIDTH - 28, 75), 1)
        pygame.draw.line(surface, _GOLD, (36, 78), (DISPLAY_WIDTH - 36, 78), 1)

        # central Pokéball
        _pokeball(surface, cx, 126, 48)

        _t(surface, self._fonts["tiny"], "GEN  I   ·   NO.  001 – 151",
           _DIM, cx, 180, bg=_CREAM)

        # ── Red footer stripe ──────────────────────────────────────────────
        pygame.draw.rect(surface, _GOLD, (0, 194, DISPLAY_WIDTH,  2))
        pygame.draw.rect(surface, RED,   (0, 196, DISPLAY_WIDTH, 44))

        _t(surface, self._fonts["tiny"], "© 1996  GAME FREAK  /  NINTENDO",
           (230, 180, 180), cx, 200, bg=RED)

        if (self._tick // 18) % 2 == 0:
            _t(surface, self._fonts["small"], "▶  PRESS A TO START  ◀",
               WHITE, cx, 214, bg=RED,
               shadow_color=_DARK_RED, shadow_offset=1)

        # outer border
        pygame.draw.rect(surface, _DARK_RED, (0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), 2)
