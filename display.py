from typing import Optional
import traceback
import os
import config

# Backlight pin (BCM numbering). Can be set via the TFT_BACKLIGHT_PIN environment variable
# or edited directly in this file. If unset or negative, backlight control is disabled.
try:
  BACKLIGHT_PIN = int(os.getenv("TFT_BACKLIGHT_PIN", "-1"))
  if BACKLIGHT_PIN < 0:
    BACKLIGHT_PIN = None
except Exception:
  BACKLIGHT_PIN = None

# Try to import RPi.GPIO if available (best-effort). GPIO will be None on non-RPi systems.
try:
  import RPi.GPIO as GPIO  # type: ignore
except Exception:
  GPIO = None

class DisplayBackend:
  def display(self, pil_image):
    """Show the given PIL Image on the device/window."""
    raise NotImplementedError

  def quit(self):
    """Optional cleanup; backends may override."""
    return None

def create_backend() -> DisplayBackend:
  """
  Create and return a suitable DisplayBackend instance.

  Tries TFT (luma) if configured, otherwise falls back to a pygame-based emulator.
  """
  if config.USE_TFT:
#     import board, digitalio, displayio, terminalio
#     from adafruit_display_text import label
#     from fourwire import FourWire
#     from adafruit_st7789 import ST7789
#     displayio.release_displays()
#     spi = board.SPI()
#     tft_cs = board.CE0
#     tft_dc = board.D24
#     reset_pin = board.D25
#     display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=reset_pin)
#     display = ST7789(display_bus, width=240, height=320, rotation=270, bgr=True, invert=False)
#     return display
#
    try:
      from luma.core.interface.serial import spi  # type: ignore
      from luma.lcd.device import st7789  # type: ignore
      from PIL import Image

      class TFTDisplay(DisplayBackend):
        def __init__(self): #, width: int = config.DISPLAY_WIDTH, height: int = config.DISPLAY_HEIGHT, rotate: int = 270):
          width_var = config.DISPLAY_WIDTH
          height_var = config.DISPLAY_HEIGHT
          rotate_var = 0
          serial = spi(port=0, device=0, gpio=None)
          self.device = st7789(serial, width=width_var, height=height_var, rotate=rotate_var)
          # store size for use when clearing on quit
          self.width = width_var
          self.height = height_var

          # Optional backlight control using RPi.GPIO (BCM numbering).
          # If BACKLIGHT_PIN is None or GPIO import failed, backlight control is disabled.
          self._backlight_pin = BACKLIGHT_PIN
          self._gpio_control = False
          if self._backlight_pin is not None and GPIO is not None:
            try:
              GPIO.setmode(GPIO.BCM)
              GPIO.setup(self._backlight_pin, GPIO.OUT, initial=GPIO.HIGH)
              self._gpio_control = True
            except Exception:
              # best-effort; don't raise if GPIO isn't usable
              self._gpio_control = False

        def display(self, pil_image):
          self.device.display(pil_image)

        def quit(self):
          """Attempt to clear the hardware display before exiting.

          This tries, in order:
          - device.clear() if available
          - sending a black PIL image to the device
          - turn off backlight GPIO (if configured)
          All exceptions are swallowed because quit should not raise during shutdown.
          """
          try:
            # If the underlying device provides a clear method, prefer that.
            if hasattr(self.device, "clear"):
              try:
                self.device.clear()
              except Exception:
                pass
            # Send a black image to ensure the panel is blanked.
            try:
              black = Image.new("RGB", (self.width, self.height), (0, 0, 0))
              self.device.display(black)
            except Exception:
              pass
            # Attempt to turn off backlight if we configured it.
            try:
              if getattr(self, "_gpio_control", False) and self._backlight_pin is not None and GPIO is not None:
                try:
                  GPIO.output(self._backlight_pin, GPIO.LOW)
                  try:
                    GPIO.cleanup(self._backlight_pin)
                  except Exception:
                    pass
                except Exception:
                  pass
            except Exception:
              pass
          except Exception:
            pass

      return TFTDisplay()
    except Exception as e:
      # Fall back to pygame if TFT initialization fails.
      print(f"Warning: failed to initialize TFT backend: {e}; falling back to pygame.")
      traceback.print_exc()

  # Pygame backend
  try:
    import pygame  # type: ignore

    class PygameDisplay(DisplayBackend):
      def __init__(self, width: int = config.DISPLAY_WIDTH, height: int = config.DISPLAY_HEIGHT):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("TFT Emulator")
        self.width = width
        self.height = height
        self.pygame = pygame

      def display(self, pil_image):
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        surf = self.pygame.image.fromstring(data, size, mode).convert()
        self.screen.blit(surf, (0, 0))
        self.pygame.display.flip()

      def quit(self):
        try:
          # Blank the pygame window before quitting so an emulator window doesn't
          # leave visible content after the process exits.
          try:
            self.screen.fill((0, 0, 0))
            self.pygame.display.flip()
          except Exception:
            pass
          self.pygame.quit()
        except Exception:
          pass

    return PygameDisplay()
  except Exception as e:
    raise RuntimeError(f"No suitable display backend available: {e}")
