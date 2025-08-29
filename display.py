from typing import Optional
import traceback
import config

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
    try:
      from luma.core.interface.serial import spi  # type: ignore
      from luma.lcd.device import st7789, ili9341  # type: ignore

      class TFTDisplay(DisplayBackend):
        def __init__(self, driver: str = "st7789", width: int = config.DISPLAY_WIDTH, height: int = config.DISPLAY_HEIGHT, rotate: int = 90):
          serial = spi(port=0, device=0, gpio=None)
          if driver == "st7789":
            self.device = st7789(serial, width=width, height=height, rotate=rotate)
          else:
            self.device = ili9341(serial, width=width, height=height, rotate=rotate)

        def display(self, pil_image):
          self.device.display(pil_image)

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
          self.pygame.quit()
        except Exception:
          pass

    return PygameDisplay()
  except Exception as e:
    raise RuntimeError(f"No suitable display backend available: {e}")
