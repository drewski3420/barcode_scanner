import os
from typing import Any

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

def _parse_bool(val: Any) -> bool:
  if isinstance(val, str):
    return val.strip().lower() in ("1", "true", "yes", "on")
  return bool(val)

TIMEOUT_MINUTES = float("20")
HOST_URL = "https://records.thejowers.com"
HID_DEVICE="/dev/input/event0"
DISPLAY_WIDTH = int("320")
DISPLAY_HEIGHT = int("240")
DISPLAY_ROTATION = int("2") # (0, 1=90, 2=180, 3=270)
DC_PIN = 25
RST_PIN = 24
#TFT_BACKLIGHT_PIN = -1
#USE_TFT = bool("true")
