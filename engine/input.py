"""
Input abstraction.

Maps both the development keyboard (Mac) and the ATtiny USB HID keyboard
(Pi) to a common set of logical buttons.

ATtiny key mapping (configure to match whatever scancodes your firmware sends):
    UP    → arrow up
    DOWN  → arrow down
    LEFT  → arrow left
    RIGHT → arrow right
    A     → return / z
    B     → backspace / x
    START → escape
    SELECT→ tab
"""

import pygame
from dataclasses import dataclass, field
from enum import Enum, auto


class Button(Enum):
    UP     = auto()
    DOWN   = auto()
    LEFT   = auto()
    RIGHT  = auto()
    A      = auto()   # confirm / select
    B      = auto()   # back / cancel
    START  = auto()
    SELECT = auto()


_KEY_MAP: dict[int, Button] = {
    pygame.K_UP:        Button.UP,
    pygame.K_DOWN:      Button.DOWN,
    pygame.K_LEFT:      Button.LEFT,
    pygame.K_RIGHT:     Button.RIGHT,
    pygame.K_RETURN:    Button.A,
    pygame.K_z:         Button.A,
    pygame.K_BACKSPACE: Button.B,
    pygame.K_x:         Button.B,
    pygame.K_ESCAPE:    Button.START,
    pygame.K_TAB:       Button.SELECT,
}


@dataclass
class InputState:
    pressed:  set[Button] = field(default_factory=set)   # held this frame
    just_down: set[Button] = field(default_factory=set)  # newly pressed
    just_up:   set[Button] = field(default_factory=set)  # newly released
    quit:      bool = False


def poll() -> InputState:
    state = InputState()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.quit = True
        elif event.type == pygame.KEYDOWN:
            btn = _KEY_MAP.get(event.key)
            if btn:
                state.just_down.add(btn)
                state.pressed.add(btn)
        elif event.type == pygame.KEYUP:
            btn = _KEY_MAP.get(event.key)
            if btn:
                state.just_up.add(btn)
                state.pressed.discard(btn)
    return state
