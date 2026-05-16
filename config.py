import os
import sys

# Native display resolution (matches physical TFT)
DISPLAY_WIDTH  = 240
DISPLAY_HEIGHT = 240

# Scale factor: 1 on Pi, >1 for comfortable dev on a desktop monitor
SCALE = 1 if os.environ.get("POKEDEX_SCALE") is None else int(os.environ["POKEDEX_SCALE"])
if SCALE == 1 and sys.platform != "linux":
    SCALE = 3   # default 720x720 window on Mac/Windows

WINDOW_WIDTH  = DISPLAY_WIDTH  * SCALE
WINDOW_HEIGHT = DISPLAY_HEIGHT * SCALE

# Pi Zero 1.1 W (armv6l, single-core) can't sustain 30fps through the
# numpy RGB565 conversion + SPI transfer; 20fps keeps it smooth.
FPS = 20 if os.uname().machine == "armv6l" else 30

# ── Palette ────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (200,  30,  30)
DARK_RED   = (120,  10,  10)
YELLOW     = (255, 220,   0)
DARK_GRAY  = ( 30,  30,  30)
MID_GRAY   = ( 80,  80,  80)
LIGHT_GRAY = (180, 180, 180)
HIGHLIGHT  = (255, 220,   0)   # selected-row accent

# ── Type colours (approximate the official palette) ─────────────────────────
TYPE_COLORS = {
    "normal":   (168, 168, 120),
    "fire":     (240, 128,  48),
    "water":    (104, 144, 240),
    "electric": (248, 208,  48),
    "grass":    (120, 200,  80),
    "ice":      (152, 216, 216),
    "fighting": (192,  48,  40),
    "poison":   (160,  64, 160),
    "ground":   (224, 192,  80),
    "flying":   (168, 144, 240),
    "psychic":  (248,  88, 136),
    "bug":      (168, 184,  32),
    "rock":     (184, 160,  56),
    "ghost":    (112,  88, 152),
    "dragon":   ( 64,  56, 184),
    "dark":     (112,  88,  72),
    "steel":    (184, 184, 208),
    "fairy":    (240, 182, 188),
}

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
CRIES_DIR   = os.path.join(ASSETS_DIR, "cries")
DB_PATH     = os.path.join(BASE_DIR, "data", "pokedex.db")
