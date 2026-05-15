# Pokédex

A software revival of the 1999 Tiger Electronics Pokémon Pokédex, running on a Raspberry Pi Zero 2 W with a 240×240 Adafruit TFT (ST7789) replacing the original LCD.

## Hardware

| Component | Part |
|-----------|------|
| Shell | Tiger Electronics Pokédex (1999) |
| SBC | Raspberry Pi Zero 2 W |
| Display | Adafruit 1.3" 240×240 TFT (ST7789, SPI) |
| Keyboard | Original PCB re-routed through custom PCB; scanned by ATtiny1614 over USB HID |
| Audio | Original speaker wired to Pi audio output |

## Software architecture

```
main.py                 Entry point — game loop
config.py               Constants: resolution, scale factor, palette, paths

data/
  fetch.py              One-time setup: pulls Gen-1 data from PokéAPI → SQLite + assets
  db.py                 SQLite query layer (Pokemon dataclass, get_all/get_by_id/search)

engine/
  display.py            Pygame surface abstraction (scaled window on dev, /dev/fb0 on Pi)
  input.py              Keyboard → Button enum (UP/DOWN/A/B/START/SELECT)
  sound.py              Pokémon cry playback via pygame.mixer

screens/
  base.py               Screen ABC: update(state) → Screen | None, draw(surface)
  home.py               Title / splash screen
  browse.py             Scrollable list of all 151 Pokémon
  detail.py             3-page detail view: info · stats · description
```

The display runs natively at 240×240. On a development machine it auto-scales 3× (720×720 window) so you can work without the physical hardware.

## Setup

### Dependencies

Requires Python 3.11–3.13 (pygame has no wheel for 3.14 yet).

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Fetch Pokémon data

Downloads sprites, cries, and stats for all 151 Gen-1 Pokémon from [PokéAPI](https://pokeapi.co). Takes ~10 minutes (rate-limited out of courtesy to the free API).

```bash
python -m data.fetch
```

### Run (development — Mac/Linux desktop)

```bash
python main.py
```

### Run (Raspberry Pi — ST7789 framebuffer)

Add to `/boot/config.txt` (adjust pins to your wiring):

```ini
dtoverlay=st7789v,speed=64000000,rotate=0,width=240,height=240
```

Then launch:

```bash
POKEDEX_SCALE=1 \
SDL_FBDEV=/dev/fb0 \
SDL_VIDEODRIVER=fbcon \
SDL_NOMOUSE=1 \
python main.py
```

## Controls

| Physical key | Dev key | Action |
|---|---|---|
| D-pad up/down | `↑` `↓` | Navigate list; prev/next Pokémon in detail |
| D-pad left/right | `←` `→` | Flip detail pages |
| A | `Enter` or `Z` | Select / next page |
| B | `Backspace` or `X` | Back |
| START | `Escape` | Return to home |

## Detail pages

Each Pokémon detail view has three swipeable pages:

1. **Info** — sprite, type badges, category, height, weight
2. **Stats** — HP / ATK / DEF / SPD / SPA / SPD bars (colour-coded)
3. **Description** — original Red/Blue Pokédex flavour text

## Project status

- [x] Core game loop (display, input, sound abstractions)
- [x] PokéAPI data fetch + SQLite storage
- [x] Home, browse, and detail screens
- [ ] Search / filter screen
- [ ] Quiz mode (silhouette / cry identification)
- [ ] Battle simulation
- [ ] ATtiny1614 firmware (keyboard scanner)
- [ ] Pi OS image + auto-start service
