import pygame
from screens.base import Screen
from engine.input import InputState, Button
from config import (DISPLAY_WIDTH, DISPLAY_HEIGHT,
                    BLACK, WHITE, RED, YELLOW, DARK_GRAY, MID_GRAY, HIGHLIGHT,
                    TYPE_COLORS)
import data.db as db


_ROW_HEIGHT   = 18
_VISIBLE_ROWS = DISPLAY_HEIGHT // _ROW_HEIGHT   # 13
_HEADER_H     = 20


class BrowseScreen(Screen):
    def __init__(self, fonts: dict) -> None:
        self._fonts   = fonts
        self._pokemon = db.get_all()
        self._cursor  = 0   # index into self._pokemon
        self._offset  = 0   # top of visible window

    # ── navigation helpers ──────────────────────────────────────────────────

    def _clamp(self) -> None:
        n = len(self._pokemon)
        self._cursor = max(0, min(n - 1, self._cursor))
        visible = _VISIBLE_ROWS - 1   # one row is the header
        if self._cursor < self._offset:
            self._offset = self._cursor
        elif self._cursor >= self._offset + visible:
            self._offset = self._cursor - visible + 1

    # ── Screen interface ────────────────────────────────────────────────────

    def update(self, state: InputState) -> Screen | None:
        if state.quit:
            return None
        if Button.START in state.just_down or Button.B in state.just_down:
            from screens.home import HomeScreen
            return HomeScreen(self._fonts)
        if Button.UP in state.just_down:
            self._cursor -= 1
            self._clamp()
        if Button.DOWN in state.just_down:
            self._cursor += 1
            self._clamp()
        if Button.A in state.just_down:
            from screens.detail import DetailScreen
            return DetailScreen(self._fonts, self._pokemon[self._cursor], self)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)

        # header bar
        pygame.draw.rect(surface, RED, (0, 0, DISPLAY_WIDTH, _HEADER_H))
        hdr = self._fonts["small"].render("POKÉDEX", True, YELLOW)
        surface.blit(hdr, (4, 3))
        count_txt = self._fonts["tiny"].render(f"{len(self._pokemon)} / 151", True, WHITE)
        surface.blit(count_txt, count_txt.get_rect(right=DISPLAY_WIDTH - 4, centery=_HEADER_H // 2))

        visible = _VISIBLE_ROWS - 1
        for i in range(visible):
            idx = self._offset + i
            if idx >= len(self._pokemon):
                break
            poke = self._pokemon[idx]
            y    = _HEADER_H + i * _ROW_HEIGHT
            selected = (idx == self._cursor)

            # row background
            row_color = HIGHLIGHT if selected else (DARK_GRAY if i % 2 == 0 else BLACK)
            pygame.draw.rect(surface, row_color, (0, y, DISPLAY_WIDTH, _ROW_HEIGHT))

            # type colour pip
            pip_color = TYPE_COLORS.get(poke.type1, MID_GRAY)
            pygame.draw.rect(surface, pip_color, (2, y + 4, 6, _ROW_HEIGHT - 8))

            # number + name
            txt_color = BLACK if selected else WHITE
            num_surf  = self._fonts["tiny"].render(f"#{poke.id:03d}", True, txt_color)
            name_surf = self._fonts["small"].render(poke.name, True, txt_color)
            surface.blit(num_surf,  (12, y + (_ROW_HEIGHT - num_surf.get_height()) // 2))
            surface.blit(name_surf, (52, y + (_ROW_HEIGHT - name_surf.get_height()) // 2))

        # scroll indicator
        total = len(self._pokemon)
        if total > visible:
            track_h = DISPLAY_HEIGHT - _HEADER_H
            thumb_h = max(10, track_h * visible // total)
            thumb_y = _HEADER_H + track_h * self._offset // total
            pygame.draw.rect(surface, MID_GRAY, (DISPLAY_WIDTH - 4, _HEADER_H, 4, track_h))
            pygame.draw.rect(surface, WHITE,    (DISPLAY_WIDTH - 4, thumb_y,  4, thumb_h))
