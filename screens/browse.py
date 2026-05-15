import pygame
from screens.base import Screen
from engine.input import InputState, Button
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, BLACK, WHITE, RED, YELLOW, TYPE_COLORS
import data.db as db

_BG       = (8,   8,  24)
_ROW_A    = (14, 14,  36)
_ROW_B    = (8,   8,  24)
_ROW_SEL  = (150, 15, 15)
_DIM      = (90,  90, 120)
_GOLD     = (210, 168,  0)

_HEADER_H = 22
_ROW_H    = 18
_VISIBLE  = (DISPLAY_HEIGHT - _HEADER_H) // _ROW_H   # 12 rows


class BrowseScreen(Screen):
    def __init__(self, fonts: dict) -> None:
        self._fonts   = fonts
        self._pokemon = db.get_all()
        self._cursor  = 0
        self._offset  = 0

    def _clamp(self) -> None:
        n = len(self._pokemon)
        self._cursor = max(0, min(n - 1, self._cursor))
        if self._cursor < self._offset:
            self._offset = self._cursor
        elif self._cursor >= self._offset + _VISIBLE:
            self._offset = self._cursor - _VISIBLE + 1

    def update(self, state: InputState) -> "Screen | None":
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
        if Button.A in state.just_down and self._pokemon:
            from screens.detail import DetailScreen
            return DetailScreen(self._fonts, self._pokemon[self._cursor], self)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(_BG)

        # ── Header ─────────────────────────────────────────────────────────
        pygame.draw.rect(surface, RED,   (0, 0, DISPLAY_WIDTH, _HEADER_H))
        pygame.draw.rect(surface, _GOLD, (0, _HEADER_H, DISPLAY_WIDTH, 1))

        hdr = self._fonts["small"].render("POKÉDEX", True, YELLOW, RED)
        surface.blit(hdr, (6, (_HEADER_H - hdr.get_height()) // 2))

        count_s = self._fonts["tiny"].render(f"{len(self._pokemon)} / 151", True, WHITE, RED)
        surface.blit(count_s, count_s.get_rect(right=DISPLAY_WIDTH - 6, centery=_HEADER_H // 2))

        # ── Rows ───────────────────────────────────────────────────────────
        for i in range(_VISIBLE):
            idx = self._offset + i
            if idx >= len(self._pokemon):
                break

            poke     = self._pokemon[idx]
            y        = _HEADER_H + 1 + i * _ROW_H
            selected = (idx == self._cursor)
            row_bg   = _ROW_SEL if selected else (_ROW_A if i % 2 == 0 else _ROW_B)

            pygame.draw.rect(surface, row_bg, (0, y, DISPLAY_WIDTH, _ROW_H))

            # type-colour strip on left edge
            pip = TYPE_COLORS.get(poke.type1, (80, 80, 80))
            pygame.draw.rect(surface, pip, (0, y, 3, _ROW_H))

            num_color  = (255, 200, 120) if selected else _DIM
            name_color = YELLOW          if selected else WHITE

            num_s  = self._fonts["tiny"].render(f"#{poke.id:03d}", True, num_color,  row_bg)
            name_s = self._fonts["small"].render(poke.name,        True, name_color, row_bg)

            cy = y + _ROW_H // 2
            surface.blit(num_s,  num_s.get_rect(left=6,  centery=cy))
            surface.blit(name_s, name_s.get_rect(left=46, centery=cy))

            # selection indicator — small triangle on right
            if selected:
                tx = DISPLAY_WIDTH - 10
                mid = cy
                pygame.draw.polygon(surface, YELLOW,
                                    [(tx, mid - 4), (tx, mid + 4), (tx + 5, mid)])

        # ── Scroll bar ─────────────────────────────────────────────────────
        total = len(self._pokemon)
        if total > _VISIBLE:
            track_y = _HEADER_H + 1
            track_h = DISPLAY_HEIGHT - track_y
            thumb_h = max(8, track_h * _VISIBLE // total)
            thumb_y = track_y + (track_h - thumb_h) * self._offset // max(1, total - _VISIBLE)
            pygame.draw.rect(surface, (25, 25, 50),  (DISPLAY_WIDTH - 3, track_y, 3, track_h))
            pygame.draw.rect(surface, RED,            (DISPLAY_WIDTH - 3, thumb_y, 3, thumb_h))
