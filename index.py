import os
import sys
import time
import select
import requests
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Optional hardware imports are lazy and optional
try:
    import RPi.GPIO as GPIO  # may be absent on non-RPi platforms
except Exception:
    GPIO = None

# Read environment with sensible parsing
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
TIMEOUT_MINUTES = float(os.getenv("TIMEOUT_MINUTES", "0.5"))
DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "320"))
DISPLAY_HEIGHT = int(os.getenv("DISPLAY_HEIGHT", "240"))
HOST_URL = os.getenv("HOST_URL", "https://records.thejowers.com")
_USE_TFT_RAW = os.getenv("USE_TFT", "false").lower()
USE_TFT = _USE_TFT_RAW in ("1", "true", "yes", "on")

# Display backend base class
class DisplayBackend:
    def display(self, pil_image):
        """Show the given PIL Image on the device/window."""
        raise NotImplementedError

# Lazily create backends to avoid import errors at module import time
def create_backend():
    if USE_TFT:
        try:
            from luma.core.interface.serial import spi
            from luma.lcd.device import st7789, ili9341

            class TFTDisplay(DisplayBackend):
                def __init__(self, driver="st7789", width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, rotate=90):
                    serial = spi(port=0, device=0, gpio=None)
                    if driver == "st7789":
                        self.device = st7789(serial, width=width, height=height, rotate=rotate)
                    else:
                        self.device = ili9341(serial, width=width, height=height, rotate=rotate)

                def display(self, pil_image):
                    self.device.display(pil_image)

            return TFTDisplay()
        except Exception as e:
            print(f"Warning: failed to initialize TFT backend: {e}; falling back to pygame.")
            # fall through to pygame
    # Pygame backend
    try:
        import pygame

        class PygameDisplay(DisplayBackend):
            def __init__(self, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT):
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

# Create backend instance
backend = create_backend()

# Fonts with fallback
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

font_huge = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font_big = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
font_small = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

def top_bar_gradient(height, start_color=(0, 34, 85), end_color=(0, 102, 204)):
    """Return a left-to-right RGB gradient PIL Image of width DISPLAY_WIDTH and given height."""
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

def fetch_cover(url):
    """Fetch an image from `url` returning an RGB PIL Image or None on failure."""
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception:
        return None

def draw_idle():
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "black")
    draw = ImageDraw.Draw(img)
    now = datetime.now().strftime("%H:%M")
    img.paste(top_bar_gradient(10), (0, 0))
    draw.text((5, 2), now, font=font_small, fill="white")
    return img

def fade_to_idle(current_img, steps=10, duration=0.5):
    """Blend current_img -> idle over steps frames and display each frame."""
    try:
        idle_img = draw_idle()
        if current_img.mode != idle_img.mode or current_img.size != idle_img.size:
            current_img = current_img.convert(idle_img.mode).resize(idle_img.size)
        for i in range(1, steps + 1):
            alpha = i / steps
            blended = Image.blend(current_img, idle_img, alpha)
            backend.display(blended)
            time.sleep(duration / steps)
    except Exception as e:
        print(f"fade_to_idle error: {e}")

def display_album(album, artist, section, code, cover_img=None):
    img = Image.new("RGB", (DISPLAY_WIDTH, DISPLAY_HEIGHT), "black")
    draw = ImageDraw.Draw(img)
    now = datetime.now().strftime("%H:%M")
    img.paste(top_bar_gradient(20), (0, 0))
    draw.text((5, 2), now, font=font_small, fill="white")
    img.paste(top_bar_gradient(20), (0, DISPLAY_HEIGHT - 20))
    draw.text((5, DISPLAY_HEIGHT - 18), "Now Playing", font=font_small, fill="white")
    y_start = 40
    spacing = 30
    draw.text((10, y_start), f"{album}", font=font_big, fill="white")
    draw.text((10, y_start + spacing), f"{artist}", font=font_big, fill="white")
    draw.text((10, y_start + 2 * spacing), f"{section}", font=font_big, fill="white")
    draw.text((10, y_start + 4 * spacing), f"{code}", font=font_huge, fill="white")

    if cover_img:
        cover_img = cover_img.resize((120, 120))
        x_cover = DISPLAY_WIDTH - 120 - 10
        y_cover = 80
        shadow = Image.new("RGB", (cover_img.width + 4, cover_img.height + 4), "grey")
        img.paste(shadow, (x_cover + 4, y_cover + 4))
        draw.rectangle([x_cover - 2, y_cover - 2, x_cover + 120 + 2, y_cover + 120 + 2], outline="white", width=2)
        img.paste(cover_img, (x_cover, y_cover))

    return img

def run_main_loop():
    print("Ready! Type a URL and press Enter (simulating QR scan)...")
    running = True
    current_data = None
    last_update = None

    try:
        while running:
            # Handle pygame events if applicable
            if not USE_TFT and hasattr(backend, "pygame"):
                for event in backend.pygame.event.get():
                    if event.type == backend.pygame.QUIT:
                        running = False

            # Timeout
            if current_data and last_update:
                if datetime.now() - last_update > timedelta(minutes=TIMEOUT_MINUTES):
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
                var_in = sys.stdin.readline().strip()
                if var_in:
                    try:
                        if len(var_in) == 6:
                            response = requests.get(f"{HOST_URL}/plays/scan/{var_in}", timeout=5)
                        else:
                            response = requests.get(var_in, timeout=5)
                        data = response.json().get('record', {})
                        album = data.get("title", "Unknown Album")
                        artist = data.get("artists", "Unknown Artist")
                        section = data.get("section", "N/A")
                        code = data.get("code", "XXXXXX")
                        cover_path = data.get("cover_path")
                        cover_img = fetch_cover(f"{HOST_URL}{cover_path}") if cover_path else None
                        current_data = (album, artist, section, code, cover_img)
                        last_update = datetime.now()
                    except Exception as e:
                        print(f"Error fetching data: {e}")
                        current_data = None

            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Cleanup pygame if used
        if not USE_TFT and hasattr(backend, "quit"):
            try:
                backend.quit()
            except Exception:
                pass

if __name__ == "__main__":
    run_main_loop()
