import os
import pygame
from screens.base import Screen
from engine.input import InputState, Button
import engine.sound as sound
from config import (DISPLAY_WIDTH, DISPLAY_HEIGHT,
                    BLACK, WHITE, RED, YELLOW, TYPE_COLORS)
import data.db as db

_BG       = (8, 8, 24)
_GOLD     = (210, 168,   0)
_DIM      = (90,  90, 120)
_DARK_RED = (100,   8,   8)
_MID_GRAY = (80,  80,  80)

_HEADER_H   = 22
_SPRITE_SIZE = 96
_STAT_BARS  = [
    ("HP",  "hp"),
    ("ATK", "attack"),
    ("DEF", "defense"),
    ("SPD", "speed"),
    ("SPA", "sp_attack"),
    ("SPD", "sp_defense"),
]
_STAT_MAX = 255


def _t(surface, font, text, color, x, y, bg, anchor="left"):
    """Render text with explicit bg (prevents SRCALPHA blit bug)."""
    s = font.render(text, True, color, bg)
    if anchor == "right":
        r = s.get_rect(right=x, top=y)
    elif anchor == "center":
        r = s.get_rect(centerx=x, top=y)
    else:
        r = s.get_rect(left=x, top=y)
    surface.blit(s, r)
    return r


class DetailScreen(Screen):
    def __init__(self, fonts: dict, pokemon: db.Pokemon, prev: Screen) -> None:
        self._fonts  = fonts
        self._poke   = pokemon
        self._prev   = prev
        self._sprite = self._load_sprite()
        self._page   = 0

        sound.play_cry(pokemon.cry_path)

    def _load_sprite(self) -> pygame.Surface | None:
        path = self._poke.sprite_path
        if not path or not os.path.exists(path):
            return None
        img = pygame.image.load(path)
        return pygame.transform.smoothscale(img, (_SPRITE_SIZE, _SPRITE_SIZE))

    # ── Screen interface ────────────────────────────────────────────────────

    def update(self, state: InputState) -> "Screen | None":
        if state.quit:
            return None
        if Button.B in state.just_down:
            sound.stop()
            return self._prev
        if Button.RIGHT in state.just_down or Button.A in state.just_down:
            self._page = (self._page + 1) % 3
        if Button.LEFT in state.just_down:
            self._page = (self._page - 1) % 3
        if Button.UP in state.just_down:
            prev = db.get_by_id(self._poke.id - 1)
            if prev:
                self._poke   = prev
                self._sprite = self._load_sprite()
                sound.play_cry(prev.cry_path)
        if Button.DOWN in state.just_down:
            nxt = db.get_by_id(self._poke.id + 1)
            if nxt:
                self._poke   = nxt
                self._sprite = self._load_sprite()
                sound.play_cry(nxt.cry_path)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)
        self._draw_header(surface)
        if self._page == 0:
            self._draw_info(surface)
        elif self._page == 1:
            self._draw_stats(surface)
        else:
            self._draw_description(surface)
        self._draw_nav(surface)

    # ── header ──────────────────────────────────────────────────────────────

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, RED,   (0, 0, DISPLAY_WIDTH, _HEADER_H))
        pygame.draw.rect(surface, _GOLD, (0, _HEADER_H, DISPLAY_WIDTH, 1))
        _t(surface, self._fonts["small"], f"#{self._poke.id:03d}",
           YELLOW, 6, 4, bg=RED)
        _t(surface, self._fonts["small"], self._poke.name.upper(),
           WHITE, DISPLAY_WIDTH - 6, 4, bg=RED, anchor="right")

    # ── info page ───────────────────────────────────────────────────────────

    def _draw_type_pill(self, surface, type_name, x, y):
        color = TYPE_COLORS.get(type_name, _MID_GRAY)
        txt   = self._fonts["tiny"].render(type_name.upper(), True, WHITE, color)
        w, h  = txt.get_width() + 8, txt.get_height() + 4
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=3)
        surface.blit(txt, (x + 4, y + 2))
        return x + w + 5

    def _draw_info(self, surface: pygame.Surface) -> None:
        cx = DISPLAY_WIDTH // 2
        sy = _HEADER_H + 4

        # sprite or placeholder
        sx = cx - _SPRITE_SIZE // 2
        if self._sprite:
            surface.blit(self._sprite, (sx, sy))
        else:
            pygame.draw.rect(surface, (20, 20, 40), (sx, sy, _SPRITE_SIZE, _SPRITE_SIZE))
            _t(surface, self._fonts["large"], "?", (60, 60, 90),
               cx, sy + _SPRITE_SIZE // 2 - 10, bg=(20, 20, 40), anchor="center")

        y = sy + _SPRITE_SIZE + 6

        # type pills
        x = 4
        for t in self._poke.types:
            x = self._draw_type_pill(surface, t, x, y)

        # category — right-aligned on same row
        if self._poke.category:
            _t(surface, self._fonts["tiny"], self._poke.category,
               _DIM, DISPLAY_WIDTH - 4, y + 2, bg=_BG, anchor="right")

        y += 18
        # divider
        pygame.draw.line(surface, (30, 30, 60), (4, y), (DISPLAY_WIDTH - 4, y))
        y += 6

        # height / weight in two columns
        _t(surface, self._fonts["tiny"], "HT",     _DIM,   4, y, bg=_BG)
        _t(surface, self._fonts["small"], self._poke.height_str,
           WHITE, 28, y - 1, bg=_BG)
        _t(surface, self._fonts["tiny"], "WT",     _DIM, cx + 4, y, bg=_BG)
        _t(surface, self._fonts["small"], self._poke.weight_str,
           WHITE, cx + 26, y - 1, bg=_BG)

    # ── stats page ──────────────────────────────────────────────────────────

    def _draw_stats(self, surface: pygame.Surface) -> None:
        y     = _HEADER_H + 8
        bar_x = 54
        bar_w = DISPLAY_WIDTH - bar_x - 8

        for label, attr in _STAT_BARS:
            val = getattr(self._poke, attr, 0) or 0

            _t(surface, self._fonts["tiny"], label, YELLOW,  4, y + 2, bg=_BG)
            _t(surface, self._fonts["tiny"], str(val), WHITE, 34, y + 2, bg=_BG,
               anchor="right")

            # track
            pygame.draw.rect(surface, (25, 25, 50),
                             (bar_x, y + 3, bar_w, 10), border_radius=3)
            # fill: green→yellow→red based on value
            ratio  = val / _STAT_MAX
            r      = int(255 * (1 - ratio))
            g      = int(200 * ratio)
            fill_w = max(3, int(bar_w * ratio))
            pygame.draw.rect(surface, (r, g, 0),
                             (bar_x, y + 3, fill_w, 10), border_radius=3)

            y += 22

    # ── description page ────────────────────────────────────────────────────

    def _draw_description(self, surface: pygame.Surface) -> None:
        # Pokemon name + number as a subtitle
        _t(surface, self._fonts["tiny"],
           f"No.{self._poke.id:03d}  {self._poke.name.upper()}",
           _DIM, 4, _HEADER_H + 6, bg=_BG)

        pygame.draw.line(surface, (30, 30, 60),
                         (4, _HEADER_H + 19), (DISPLAY_WIDTH - 4, _HEADER_H + 19))

        desc  = self._poke.description or "No data available."
        words = desc.split()
        lines: list[str] = []
        cur   = ""
        for word in words:
            test = (cur + " " + word).strip()
            if self._fonts["small"].size(test)[0] <= DISPLAY_WIDTH - 8:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)

        y = _HEADER_H + 26
        for line in lines:
            _t(surface, self._fonts["small"], line, WHITE, 4, y, bg=_BG)
            y += self._fonts["small"].get_linesize() + 1
            if y > DISPLAY_HEIGHT - 16:
                break

    # ── navigation dots + arrows ────────────────────────────────────────────

    def _draw_nav(self, surface: pygame.Surface) -> None:
        cx = DISPLAY_WIDTH // 2
        y  = DISPLAY_HEIGHT - 8

        # page dots
        for i in range(3):
            color = WHITE if i == self._page else (40, 40, 60)
            pygame.draw.circle(surface, color, (cx + (i - 1) * 14, y), 3)

        # subtle left/right hints
        if self._page > 0:
            pygame.draw.polygon(surface, _DIM,
                                [(8, y), (14, y - 4), (14, y + 4)])
        if self._page < 2:
            pygame.draw.polygon(surface, _DIM,
                                [(DISPLAY_WIDTH - 8, y),
                                 (DISPLAY_WIDTH - 14, y - 4),
                                 (DISPLAY_WIDTH - 14, y + 4)])
