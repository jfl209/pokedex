import math
import pygame
from screens.base import Screen
from engine.input import InputState, Button
from config import DISPLAY_WIDTH, DISPLAY_HEIGHT, BLACK, RED, YELLOW, WHITE, DARK_RED


class HomeScreen(Screen):
    def __init__(self, fonts: dict) -> None:
        self._fonts = fonts
        self._tick  = 0

    def update(self, state: InputState) -> Screen | None:
        self._tick += 1
        if state.quit:
            return None
        if Button.A in state.just_down or Button.START in state.just_down:
            from screens.browse import BrowseScreen
            return BrowseScreen(self._fonts)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)

        # red panel
        pygame.draw.rect(surface, RED, (0, 0, DISPLAY_WIDTH, 90))
        pygame.draw.rect(surface, DARK_RED, (0, 88, DISPLAY_WIDTH, 4))

        title  = self._fonts["large"].render("POKÉDEX", True, YELLOW)
        sub    = self._fonts["small"].render("KANTO EDITION", True, WHITE)
        surface.blit(title, title.get_rect(centerx=DISPLAY_WIDTH // 2, top=18))
        surface.blit(sub,   sub.get_rect(centerx=DISPLAY_WIDTH // 2, top=62))

        # Pokéball
        cx, cy, r = DISPLAY_WIDTH // 2, 150, 44

        # black border
        pygame.draw.circle(surface, BLACK, (cx, cy), r)

        # white bottom half
        pygame.draw.circle(surface, (220, 220, 220), (cx, cy), r - 2)

        # red top half — polygon tracing the upper semicircle then closing at centre
        top_half = [
            (cx + (r - 2) * math.cos(math.radians(a)),
             cy + (r - 2) * math.sin(math.radians(a)))
            for a in range(181, 360)
        ]
        top_half.append((cx, cy))
        pygame.draw.polygon(surface, RED, top_half)

        # horizontal dividing line
        pygame.draw.line(surface, BLACK, (cx - r + 2, cy), (cx + r - 2, cy), 3)

        # centre button: black ring → dark grey band → white dot
        pygame.draw.circle(surface, BLACK, (cx, cy), 10)
        pygame.draw.circle(surface, (60, 60, 60), (cx, cy), 8)
        pygame.draw.circle(surface, WHITE, (cx, cy), 5)

        # blinking prompt
        if (self._tick // 15) % 2 == 0:
            prompt = self._fonts["small"].render("PRESS  A  TO  START", True, YELLOW)
            surface.blit(prompt, prompt.get_rect(centerx=DISPLAY_WIDTH // 2, top=210))
