from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import time
import config

def load_font(path: str, size: int):
  try:
    return ImageFont.truetype(path, size)
  except Exception:
    return ImageFont.load_default()


font_huge = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font_big = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
font_small = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

def _text_size(draw, text, font):
  """Return (width, height) for text using available PIL APIs.

  Prefer ImageDraw.textsize(draw) where available. Fall back to font.getbbox()
  (returns (x0,y0,x1,y1)) or font.getmask().size. As a final fallback,
  approximate using len(text) * font.size.
  """
  try:
    return draw.textsize(text, font=font)
  except Exception:
    try:
      bbox = font.getbbox(text)
      return (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except Exception:
      try:
        mask = font.getmask(text)
        return mask.size
      except Exception:
        return (len(text) * getattr(font, "size", 10), getattr(font, "size", 10))

def top_bar_gradient(height, start_color=(0, 34, 85), end_color=(0, 102, 204)):
  """Return a left-to-right RGB gradient PIL Image of width DISPLAY_WIDTH and given height."""
  grad = Image.new("RGB", (config.DISPLAY_WIDTH, height), "#000000")
  start_r, start_g, start_b = start_color
  end_r, end_g, end_b = end_color
  for x in range(config.DISPLAY_WIDTH):
    ratio = x / (config.DISPLAY_WIDTH - 1) if config.DISPLAY_WIDTH > 1 else 0
    r = int(start_r + (end_r - start_r) * ratio)
    g = int(start_g + (end_g - start_g) * ratio)
    b = int(start_b + (end_b - start_b) * ratio)
    for y in range(height):
      grad.putpixel((x, y), (r, g, b))
  return grad

def fetch_cover_placeholder():
  """Small helper if you need a consistent placeholder image (not used automatically)."""
  img = Image.new("RGB", (120, 120), "grey")
  draw = ImageDraw.Draw(img)
  draw.text((10, 50), "No cover", fill="white")
  return img

def draw_idle():
  img = Image.new("RGB", (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), "black")
  draw = ImageDraw.Draw(img)
  now = datetime.now().strftime("%H:%M")
  img.paste(top_bar_gradient(10), (0, 0))
  draw.text((5, 2), now, font=font_small, fill="white")
  return img

def fade_to_idle(current_img, backend, steps=10, duration=0.5):
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
  img = Image.new("RGB", (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), "black")
  draw = ImageDraw.Draw(img)
  now = datetime.now().strftime("%H:%M")
  img.paste(top_bar_gradient(20), (0, 0))
  draw.text((5, 2), now, font=font_small, fill="white")
  img.paste(top_bar_gradient(20), (0, config.DISPLAY_HEIGHT - 20))
  draw.text((5, config.DISPLAY_HEIGHT - 18), "Now Playing", font=font_small, fill="white")
  # draw section on the right side of the bottom bar
  section_text = f"{section}"
  text_w, text_h = _text_size(draw, section_text, font_small)
  draw.text((config.DISPLAY_WIDTH - 10 - text_w, config.DISPLAY_HEIGHT - 18), section_text, font=font_small, fill="white")
  y_start = 40
  spacing = 30
  draw.text((10, y_start), f"{album}", font=font_big, fill="white")
  draw.text((10, y_start + spacing), f"{artist}", font=font_big, fill="white")
  draw.text((10, y_start + 4 * spacing), f"{code}", font=font_huge, fill="white")

  if cover_img:
    cover_img = cover_img.resize((120, 120))
    x_cover = config.DISPLAY_WIDTH - 120 - 10
    y_cover = 80
    shadow = Image.new("RGB", (cover_img.width + 4, cover_img.height + 4), "grey")
    img.paste(shadow, (x_cover + 4, y_cover + 4))
    draw.rectangle([x_cover - 2, y_cover - 2, x_cover + 120 + 2, y_cover + 120 + 2], outline="white", width=2)
    img.paste(cover_img, (x_cover, y_cover))

  return img
