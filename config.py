"""
config.py
Centralized environment parsing and configuration constants.

This module intentionally does minimal work and is safe to import on any platform.
"""
import os
from typing import Any

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def _parse_bool(val: Any) -> bool:
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


TIMEOUT_MINUTES = float(os.getenv("TIMEOUT_MINUTES", "0.5"))
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "320"))
DISPLAY_HEIGHT = int(os.getenv("DISPLAY_HEIGHT", "240"))
HOST_URL = os.getenv("HOST_URL", "https://records.thejowers.com")
USE_TFT = _parse_bool(os.getenv("USE_TFT", "false"))
