import pygame
from config import CRIES_DIR
import os

_initialized = False


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _initialized = True


def play_cry(cry_path: str | None) -> None:
    if not cry_path or not os.path.exists(cry_path):
        return
    _ensure_init()
    try:
        pygame.mixer.music.load(cry_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"sound: {e}")


def stop() -> None:
    if _initialized:
        pygame.mixer.music.stop()
