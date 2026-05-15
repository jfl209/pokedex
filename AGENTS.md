# Agent guidelines

This file tells AI coding agents how to work effectively in this repository.

## What this project is

A Python/Pygame application that runs on a Raspberry Pi Zero 2 W inside a modded 1999 Tiger Electronics Pokémon Pokédex shell. The display is a 240×240 ST7789 TFT; keyboard input comes from an ATtiny1614 USB HID device; audio plays through the original speaker.

All game logic runs at the native 240×240 resolution. A `SCALE` factor (default 3× on non-Linux) blows the window up for desktop development — never write layout code that assumes the window size; always use `DISPLAY_WIDTH` / `DISPLAY_HEIGHT` from `config.py`.

## Running the project

```bash
source .venv/bin/activate          # Python 3.13 venv
python -m data.fetch               # one-time: populate DB + download assets
python main.py                     # run with auto-scaled dev window
```

The venv must be Python 3.11–3.13; pygame has no wheel for 3.14.

## Architecture rules

### Screen system

Every UI view is a `Screen` subclass (`screens/base.py`). A screen's `update()` returns:
- `self` — stay on this screen
- another `Screen` instance — transition to it
- `None` — quit

Never mutate global state from inside a screen. Pass what the next screen needs as constructor arguments.

### Display

Draw only to `display.surface` (the 240×240 native surface). The `Display.flip()` call handles scaling and presenting to the window. Do not call `pygame.display.flip()` directly.

### Input

Use the `Button` enum and `InputState` from `engine/input.py`. Check `just_down` for one-shot actions (select, back) and `pressed` for held actions (scroll acceleration if added). Do not read `pygame.key.get_pressed()` directly in screen code.

### Data

`data/db.py` is the only place that touches SQLite. Screen code calls `db.get_all()`, `db.get_by_id()`, or `db.search_by_name()` — it never constructs queries itself.

`data/fetch.py` is a one-time CLI script, not a library. Do not import it from application code.

### Sound

Use `engine/sound.py` (`play_cry`, `stop`). Do not call pygame.mixer directly from screen code.

## Style

- No comments unless the why is non-obvious.
- No docstrings on short functions.
- Prefer `|` union syntax for type hints (`Screen | None`, not `Optional[Screen]`).
- All pixel measurements in native units (0–239), never scaled units.
- Colours come from `config.py` — do not hardcode RGB tuples in screen files.

## Adding a new screen

1. Create `screens/my_screen.py` subclassing `Screen`.
2. Implement `update(state) → Screen | None` and `draw(surface)`.
3. Import lazily inside `update()` (to avoid circular imports) when returning a new screen instance.
4. Pass `fonts` dict through from `main.py` — do not call `pygame.font` inside a screen.

## What not to do

- Do not add network calls to the runtime path; all data must be local after `data.fetch` runs.
- Do not use `pygame.display.set_mode()` outside `engine/display.py`.
- Do not scale coordinates manually; draw at native resolution and let `Display` handle it.
- Do not create new SQLite connections; use the module-level connection in `data/db.py`.
