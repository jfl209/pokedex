import os
import pygame
from screens.base import Screen
from engine.input import InputState, Button
import engine.sound as sound
from config import (DISPLAY_WIDTH, DISPLAY_HEIGHT,
                    BLACK, WHITE, RED, YELLOW, DARK_GRAY, MID_GRAY, LIGHT_GRAY,
                    TYPE_COLORS)
import data.db as db

_SPRITE_SIZE = 96
_STAT_BARS   = [("HP", "hp"), ("ATK", "attack"), ("DEF", "defense"),
                ("SPD", "speed"), ("SPA", "sp_attack"), ("SPD", "sp_defense")]
_STAT_MAX    = 255


class DetailScreen(Screen):
    def __init__(self, fonts: dict, pokemon: db.Pokemon, prev: Screen) -> None:
        self._fonts   = fonts
        self._poke    = pokemon
        self._prev    = prev
        self._sprite: pygame.Surface | None = self._load_sprite()
        self._page    = 0   # 0 = info, 1 = stats, 2 = description

        sound.play_cry(pokemon.cry_path)

    def _load_sprite(self) -> pygame.Surface | None:
        path = self._poke.sprite_path
        if not path or not os.path.exists(path):
            return None
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (_SPRITE_SIZE, _SPRITE_SIZE))
        return img

    # ── Screen interface ────────────────────────────────────────────────────

    def update(self, state: InputState) -> Screen | None:
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
            # navigate to previous pokemon
            nxt = db.get_by_id(self._poke.id - 1)
            if nxt:
                self._poke   = nxt
                self._sprite = self._load_sprite()
                sound.play_cry(nxt.cry_path)
        if Button.DOWN in state.just_down:
            nxt = db.get_by_id(self._poke.id + 1)
            if nxt:
                self._poke   = nxt
                self._sprite = self._load_sprite()
                sound.play_cry(nxt.cry_path)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self._draw_header(surface)
        if self._page == 0:
            self._draw_info(surface)
        elif self._page == 1:
            self._draw_stats(surface)
        else:
            self._draw_description(surface)
        self._draw_page_dots(surface)

    # ── drawing helpers ─────────────────────────────────────────────────────

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, RED, (0, 0, DISPLAY_WIDTH, 20))
        num  = self._fonts["small"].render(f"#{self._poke.id:03d}", True, YELLOW)
        name = self._fonts["small"].render(self._poke.name.upper(), True, WHITE)
        surface.blit(num,  (4, 3))
        surface.blit(name, name.get_rect(right=DISPLAY_WIDTH - 4, top=3))

    def _draw_type_badge(self, surface: pygame.Surface, type_name: str, x: int, y: int) -> int:
        color    = TYPE_COLORS.get(type_name, MID_GRAY)
        txt      = self._fonts["tiny"].render(type_name.upper(), True, WHITE)
        w        = txt.get_width() + 8
        h        = txt.get_height() + 4
        pygame.draw.rect(surface, color, (x, y, w, h), border_radius=3)
        surface.blit(txt, (x + 4, y + 2))
        return x + w + 4

    def _draw_info(self, surface: pygame.Surface) -> None:
        # sprite
        sx = (DISPLAY_WIDTH - _SPRITE_SIZE) // 2
        if self._sprite:
            surface.blit(self._sprite, (sx, 22))
        else:
            pygame.draw.rect(surface, DARK_GRAY, (sx, 22, _SPRITE_SIZE, _SPRITE_SIZE))
            q = self._fonts["large"].render("?", True, MID_GRAY)
            surface.blit(q, q.get_rect(centerx=DISPLAY_WIDTH // 2, centery=22 + _SPRITE_SIZE // 2))

        # type badges
        x = 4
        for t in self._poke.types:
            x = self._draw_type_badge(surface, t, x, 124)

        if self._poke.category:
            cat = self._fonts["tiny"].render(self._poke.category, True, LIGHT_GRAY)
            surface.blit(cat, cat.get_rect(right=DISPLAY_WIDTH - 4, top=125))

        # height / weight
        y = 142
        for label, val in (("HT", self._poke.height_str), ("WT", self._poke.weight_str)):
            lbl_s = self._fonts["tiny"].render(f"{label}:", True, YELLOW)
            val_s = self._fonts["small"].render(val, True, WHITE)
            surface.blit(lbl_s, (4, y))
            surface.blit(val_s, (30, y - 1))
            y += 18

    def _draw_stats(self, surface: pygame.Surface) -> None:
        y = 28
        bar_x = 52
        bar_w = DISPLAY_WIDTH - bar_x - 8

        for label, attr in _STAT_BARS:
            val = getattr(self._poke, attr, 0) or 0

            lbl_s = self._fonts["tiny"].render(label, True, YELLOW)
            surface.blit(lbl_s, (4, y + 2))

            num_s = self._fonts["tiny"].render(str(val), True, WHITE)
            surface.blit(num_s, (34, y + 2))

            # background track
            pygame.draw.rect(surface, DARK_GRAY, (bar_x, y + 4, bar_w, 10), border_radius=3)
            # filled portion — colour shifts red→yellow→green
            ratio = val / _STAT_MAX
            r = int(255 * (1 - ratio))
            g = int(255 * ratio)
            fill_w = max(2, int(bar_w * ratio))
            pygame.draw.rect(surface, (r, g, 0), (bar_x, y + 4, fill_w, 10), border_radius=3)

            y += 22

    def _draw_description(self, surface: pygame.Surface) -> None:
        desc = self._poke.description or "No data available."
        words = desc.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if self._fonts["small"].size(test)[0] <= DISPLAY_WIDTH - 8:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = 28
        for line in lines:
            txt = self._fonts["small"].render(line, True, WHITE)
            surface.blit(txt, (4, y))
            y += self._fonts["small"].get_linesize()
            if y > DISPLAY_HEIGHT - 20:
                break

    def _draw_page_dots(self, surface: pygame.Surface) -> None:
        cx = DISPLAY_WIDTH // 2
        y  = DISPLAY_HEIGHT - 8
        for i in range(3):
            color = WHITE if i == self._page else MID_GRAY
            pygame.draw.circle(surface, color, (cx + (i - 1) * 14, y), 3)
