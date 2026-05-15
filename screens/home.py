import math
import random
import pygame
from screens.base import Screen
from engine.input import InputState, Button
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, BLACK, RED, YELLOW, WHITE

_BG       = (8, 8, 24)    # dark navy
_SHADOW   = (0, 0, 0)
_DIM      = (70, 70, 110)
_VERY_DIM = (38, 38, 62)
_RED_DARK = (100, 8, 8)


def _t(surface, font, text, color, cx, y, shadow_color=None, shadow_offset=1):
    """
    Render text centred at cx, top at y.
    Passing shadow_color draws a drop-shadow at (+offset, +offset).
    Returns the bottom y of the rendered text.
    Uses an explicit background so the returned surface is not SRCALPHA,
    avoiding a pygame/macOS blit bug where text lands with alpha=0.
    """
    if shadow_color is not None:
        shad = font.render(text, True, shadow_color, _BG)
        r    = shad.get_rect(centerx=cx + shadow_offset, top=y + shadow_offset)
        surface.blit(shad, r)
    main = font.render(text, True, color, _BG)
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
        rng = random.Random(42)
        self._stars = [
            (rng.randint(3, DISPLAY_WIDTH - 3),
             rng.randint(3, DISPLAY_HEIGHT - 3),
             rng.choice([1, 1, 1, 2]),
             rng.random() * 2 * math.pi)
            for _ in range(60)
        ]

    def update(self, state: InputState) -> "Screen | None":
        self._tick += 1
        if state.quit:
            return None
        if Button.A in state.just_down or Button.START in state.just_down:
            from screens.browse import BrowseScreen
            return BrowseScreen(self._fonts)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)

        cx = DISPLAY_WIDTH // 2

        # twinkling starfield
        for sx, sy, sz, phase in self._stars:
            b = int(130 + 100 * math.sin(self._tick * 0.05 + phase))
            pygame.draw.circle(surface, (b, b, min(255, b + 50)), (sx, sy), sz)

        # screen border
        pygame.draw.rect(surface, RED, (0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT), 2)

        # title
        y = _t(surface, self._fonts["title"], "POKÉDEX",
               YELLOW, cx, 11,
               shadow_color=_RED_DARK, shadow_offset=2)

        # subtitle — spaced out for classic Game Boy feel
        y = _t(surface, self._fonts["small"], "K A N T O   E D I T I O N",
               WHITE, cx, y + 5,
               shadow_color=_SHADOW, shadow_offset=1)

        # decorative divider
        y += 7
        bw = 110
        pygame.draw.line(surface, RED,      (cx - bw // 2,     y),     (cx + bw // 2,     y),     1)
        pygame.draw.line(surface, _DIM,     (cx - bw // 2 + 4, y + 3), (cx + bw // 2 - 4, y + 3), 1)

        # Pokéball
        _pokeball(surface, cx, 136, 52)

        # generation label
        _t(surface, self._fonts["tiny"], "GEN  I   ·   NO.  001 – 151", _DIM, cx, 194)

        # blinking prompt
        if (self._tick // 18) % 2 == 0:
            _t(surface, self._fonts["small"], "▶  PRESS A TO START  ◀",
               YELLOW, cx, 208, shadow_color=_SHADOW, shadow_offset=1)

        # copyright
        _t(surface, self._fonts["tiny"], "© 1996  GAME FREAK  /  NINTENDO", _VERY_DIM, cx, 226)
