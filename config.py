import os
from typing import Any

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

def _parse_bool(val: Any) -> bool:
  if isinstance(val, str):
    return val.strip().lower() in ("1", "true", "yes", "on")
  return bool(val)

TIMEOUT_MINUTES = float("0.5")
DISPLAY_WIDTH = int("320")
DISPLAY_HEIGHT = int("240")
HOST_URL = "https://records.thejowers.com"
USE_TFT = bool("true")
HID_DEVICE="/dev/input/event0"
