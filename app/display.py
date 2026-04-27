import traceback
import config

from RPi import GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from PIL import Image, ImageDraw

class DisplayBackend:
  def display(self, pil_image):
    """Show the given PIL Image on the device/window."""
    raise NotImplementedError

  def quit(self):
    """Optional cleanup; backends may override."""
    return None

def create_backend() -> DisplayBackend:
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)

  class TFTDisplay(DisplayBackend):
    def __init__(self):
      width_var = config.DISPLAY_WIDTH
      height_var = config.DISPLAY_HEIGHT
      rotate_var = config.DISPLAY_ROTATION
      dc_pin = config.DC_PIN
      rst_pin = config.RST_PIN
      serial = spi(port=0, device=0, gpio=GPIO, bus_speed_hz=8000000, gpio_DC=dc_pin, gpio_RST=rst_pin)
      self.device = st7789(serial_interface=serial, width=width_var, height=height_var, rotate=rotate_var)

    def display(self, pil_image):
      self.device.display(pil_image)

    def quit(self):
      """Attempt to clear the hardware display before exiting."""
      try:
      # If the underlying device provides a clear method, prefer that.
        if hasattr(self.device, "clear"):
          try:
            self.device.clear()
          except Exception:
            pass
        # Send a black image to ensure the panel is blanked.
        try:
          black = Image.new("RGB", (width_var, height_var), (0, 0, 0))
          self.device.display(black)
        except Exception:
          pass
      except Exception:
        pass
  return TFTDisplay()
