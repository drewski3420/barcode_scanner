import requests
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import sys, time, select

# --- Global State ---
last_update = None
current_data = None
TIMEOUT_MINUTES = 0.1
DISPLAY_WIDTH, DISPLAY_HEIGHT = 320, 240

# Optional backends
use_tft = False  # Set True when hardware is available

# --- Display Backend Interface ---
class DisplayBackend:
  def display(self, pil_image):
    """Show the given PIL image"""
    raise NotImplementedError

# --- TFT Backend ---
if use_tft:
  from luma.core.interface.serial import spi
  from luma.lcd.device import st7789, ili9341

  class TFTDisplay(DisplayBackend):
    def __init__(self, driver='st7789', width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotate=90):
      serial = spi(port=0, device=0, gpio=None)
      if driver == 'st7789':
        self.device = st7789(serial, width=width, height=height, rotate=rotate)
      else:
        self.device = ili9341(serial, width=width, height=height, rotate=rotate)

    def display(self, pil_image):
      self.device.display(pil_image)

# --- Pygame Backend ---
else:
  import pygame
  class PygameDisplay(DisplayBackend):
    def __init__(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT):
      pygame.init()
      self.screen = pygame.display.set_mode((width, height))
      pygame.display.set_caption("TFT Emulator")
      self.width = width
      self.height = height

    def display(self, pil_image):
      mode = pil_image.mode
      size = pil_image.size
      data = pil_image.tobytes()
      surf = pygame.image.fromstring(data, size, mode).convert()
      self.screen.blit(surf, (0, 0))
      pygame.display.flip()

# --- Choose backend ---
backend = TFTDisplay() if use_tft else PygameDisplay()

# --- Fonts ---
font_huge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

# Changes: Added top_bar_gradient() and replaced the previous solid 'darkblue' top-bar rectangles
# with a left-to-right gradient image that is pasted into the main image. This keeps the public
# function interfaces unchanged and only affects the appearance of the top bar.
def top_bar_gradient(height, start_color=(0, 34, 85), end_color=(0, 102, 204)):
  """Return an Image (width=DISPLAY_WIDTH, height=height) with a left-to-right RGB gradient.

  The function constructs the gradient per-column and returns a PIL Image that can be
  pasted at (0,0) to draw the top bar. Colors are given as RGB tuples; defaults are
  a dark blue -> lighter blue transition.
  """
  grad = Image.new("RGB", (DISPLAY_WIDTH, height), "#000000")
  start_r, start_g, start_b = start_color
  end_r, end_g, end_b = end_color
  for x in range(DISPLAY_WIDTH):
    ratio = x / (DISPLAY_WIDTH - 1) if DISPLAY_WIDTH > 1 else 0
    r = int(start_r + (end_r - start_r) * ratio)
    g = int(start_g + (end_g - start_g) * ratio)
    b = int(start_b + (end_b - start_b) * ratio)
    for y in range(height):
      grad.putpixel((x, y), (r, g, b))
  return grad

# --- Fetch Cover Image ---
def fetch_cover(url):
  try:
    print(url)
    resp = requests.get(url, timeout=5)

    print(resp.status_code)
    return Image.open(BytesIO(resp.content)).convert("RGB")
  except Exception:
    return None

# --- Draw Idle Screen ---
def draw_idle():
  img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "black")
  draw = ImageDraw.Draw(img)
  now = datetime.now().strftime("%H:%M")
  # Top bar (gradient)
  img.paste(top_bar_gradient(10), (0,0))
  draw.text((5, 2), now, font=font_small, fill="white")
  return img

def fade_to_idle(current_img, steps=10, duration=0.5):
  """
  Fade from current_img to the idle screen over `steps` frames spanning `duration` seconds.

  This creates blended intermediate images using PIL.Image.blend and displays each frame
  via the selected backend. If an error occurs during fading we print it and return.
  """
  try:
    idle_img = draw_idle()
    # Ensure modes and sizes match
    if current_img.mode != idle_img.mode or current_img.size != idle_img.size:
      current_img = current_img.convert(idle_img.mode).resize(idle_img.size)

    for i in range(1, steps + 1):
      alpha = i / steps
      blended = Image.blend(current_img, idle_img, alpha)
      backend.display(blended)
      time.sleep(duration / steps)
  except Exception as e:
    print(f"fade_to_idle error: {e}")

# --- Draw Now Playing ---
def display_album(album, artist, section, code, cover_img=None):
  img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "black")
  draw = ImageDraw.Draw(img)
  now = datetime.now().strftime("%H:%M")

  # Top bar (gradient)
  img.paste(top_bar_gradient(20), (0,0))
  draw.text((5, 2), now, font=font_small, fill="white")

  # Bottom bar (gradient)
  img.paste(top_bar_gradient(20), (0, DISPLAY_HEIGHT - 20))
  draw.text((5, DISPLAY_HEIGHT - 18), "Now Playing", font=font_small, fill="white")

  # Left side text
  y_start = 40
  spacing = 30
  draw.text((10, y_start), f"{album}", font=font_big, fill="white")
  draw.text((10, y_start + spacing), f"{artist}", font=font_big, fill="white")
  draw.text((10, y_start + 2*spacing), f"{section}", font=font_big, fill="white")
  draw.text((10, y_start + 4*spacing), f"{code}", font=font_huge, fill="white")

  # Right cover image
  if cover_img:
    cover_img = cover_img.resize((120, 120))
    x_cover = DISPLAY_WIDTH - 120 - 10
    y_cover = 40

    # Shadow
    shadow = Image.new("RGB", (cover_img.width + 4, cover_img.height + 4), "grey")
    img.paste(shadow, (x_cover + 4, y_cover + 4))

    # White frame
    draw.rectangle([x_cover - 2, y_cover - 2, x_cover + 120 + 2, y_cover + 120 + 2], outline="white", width=2)

    # Paste cover
    img.paste(cover_img, (x_cover, y_cover))

  return img

# --- Main Loop ---
print("Ready! Type a URL and press Enter (simulating QR scan)...")
running = True

while running:
  try:
    # Handle hardware window events (pygame)
    if not use_tft:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False

    # Timeout
    if current_data and last_update:
      if datetime.now() - last_update > timedelta(minutes=TIMEOUT_MINUTES):
        # Fade the current display to the idle screen before clearing state
        try:
          album, artist, section, code, cover_img = current_data
          curr_img = display_album(album, artist, section, code, cover_img)
          fade_to_idle(curr_img)
        except Exception as e:
          print(f"Error during fade to idle: {e}")
        current_data = None
        last_update = None

    # Draw
    if not current_data:
      backend.display(draw_idle())
    else:
      album, artist, section, code, cover_img = current_data
      backend.display(display_album(album, artist, section, code, cover_img))

    # Non-blocking input
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
      url = sys.stdin.readline().strip()
      if url:
        try:
          if len(url) == 6:
            response = requests.get(f"http://localhost:3021/plays/scan/{url}", timeout=5)
          else:
            response = requests.get(url, timeout=5)
          data = response.json()['record']
          album = data.get("title", "Unknown Album")
          artist = data.get("artists", "Unknown Artist")
          section = data.get("section", "N/A")
          code = data.get("code", "XXXXXX")
          cover_url = f"http://localhost:3021{data.get('cover_path')}"
          cover_img = fetch_cover(cover_url) if cover_url else None
          current_data = (album, artist, section, code, cover_img)
          last_update = datetime.now()
        except Exception as e:
          print(f"Error fetching data: {e}")
          current_data = None

    time.sleep(0.1)

  except Exception as e:
    print(f"Error in main loop: {e}")
    current_data = None

if not use_tft:
  import pygame
  pygame.quit()
