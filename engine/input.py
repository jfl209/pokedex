"""
Input abstraction.

On Mac/dev:  reads pygame keyboard events (normal windowed SDL behaviour).
On Pi/Linux: reads evdev events directly from /dev/input/event* in a
             background thread — works without a pygame display window and
             automatically picks up the ATtiny USB HID keyboard as well as
             any uinput virtual devices used for testing.

Evdev key → Button mapping (matches ATtiny HID firmware defaults):
    KEY_UP        → UP
    KEY_DOWN      → DOWN
    KEY_LEFT      → LEFT
    KEY_RIGHT     → RIGHT
    KEY_ENTER     → A
    KEY_BACKSPACE → B
    KEY_ESC       → START
    KEY_TAB       → SELECT
"""

import sys
import queue
import threading
import pygame
from dataclasses import dataclass, field
from enum import Enum, auto


class Button(Enum):
    UP     = auto()
    DOWN   = auto()
    LEFT   = auto()
    RIGHT  = auto()
    A      = auto()
    B      = auto()
    START  = auto()
    SELECT = auto()


# ── pygame key map (Mac / windowed dev) ────────────────────────────────────
_PYGAME_MAP: dict[int, Button] = {
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

# ── evdev key code map (Pi / Linux) ────────────────────────────────────────
_EVDEV_MAP: dict[int, Button] = {
    103: Button.UP,       # KEY_UP
    108: Button.DOWN,     # KEY_DOWN
    105: Button.LEFT,     # KEY_LEFT
    106: Button.RIGHT,    # KEY_RIGHT
    28:  Button.A,        # KEY_ENTER
    14:  Button.B,        # KEY_BACKSPACE
    1:   Button.START,    # KEY_ESC
    15:  Button.SELECT,   # KEY_TAB
}


@dataclass
class InputState:
    pressed:   set[Button] = field(default_factory=set)
    just_down: set[Button] = field(default_factory=set)
    just_up:   set[Button] = field(default_factory=set)
    quit:      bool = False


# ── evdev background thread (Pi only) ──────────────────────────────────────

_evdev_q:      queue.Queue = queue.Queue()
_evdev_thread: threading.Thread | None = None
_held:         set[Button] = set()


def _evdev_loop() -> None:
    """Watch all /dev/input/event* devices for keyboard events."""
    import evdev, select, time

    known: dict[str, evdev.InputDevice] = {}

    while True:
        # Discover any new keyboard-capable devices (catches hotplug)
        for path in evdev.list_devices():
            if path not in known:
                try:
                    dev = evdev.InputDevice(path)
                    if evdev.ecodes.EV_KEY in dev.capabilities():
                        known[path] = dev
                        print(f"input: watching {path} ({dev.name})")
                except Exception:
                    pass

        if not known:
            time.sleep(0.5)
            continue

        devs = list(known.values())
        try:
            readable, _, _ = select.select(devs, [], [], 0.1)
        except (OSError, ValueError):
            known = {p: d for p, d in known.items()
                     if d.fileno() >= 0}
            continue

        for dev in readable:
            try:
                for ev in dev.read():
                    if ev.type == evdev.ecodes.EV_KEY:
                        btn = _EVDEV_MAP.get(ev.code)
                        if btn:
                            _evdev_q.put((btn, ev.value))  # value 1=down 0=up
            except OSError:
                known.pop(dev.path, None)


def _ensure_evdev() -> None:
    global _evdev_thread
    if _evdev_thread is None:
        _evdev_thread = threading.Thread(
            target=_evdev_loop, daemon=True, name="evdev-input"
        )
        _evdev_thread.start()


# ── public poll() ───────────────────────────────────────────────────────────

def poll() -> InputState:
    state = InputState()

    if sys.platform == "linux":
        _ensure_evdev()

        # Drain the evdev event queue
        while True:
            try:
                btn, value = _evdev_q.get_nowait()
                if value == 1:           # key down
                    state.just_down.add(btn)
                    _held.add(btn)
                elif value == 0:         # key up
                    state.just_up.add(btn)
                    _held.discard(btn)
                # value == 2 is key repeat — treat as held, not just_down
            except queue.Empty:
                break

        state.pressed = set(_held)

        # Still drain pygame quit events so Ctrl+C works
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.quit = True

    else:
        # Mac / windowed: use pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.quit = True
            elif event.type == pygame.KEYDOWN:
                btn = _PYGAME_MAP.get(event.key)
                if btn:
                    state.just_down.add(btn)
                    _held.add(btn)
            elif event.type == pygame.KEYUP:
                btn = _PYGAME_MAP.get(event.key)
                if btn:
                    state.just_up.add(btn)
                    _held.discard(btn)

        state.pressed = set(_held)

    return state
