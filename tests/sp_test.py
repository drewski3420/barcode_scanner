import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Display bus setup
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D24)
reset_pin = digitalio.DigitalInOut(board.D25)

# Create the display bus (FourWire)
from adafruit_rgb_display.rgb import color565
from adafruit_rgb_display.st7789 import ST7789
from adafruit_rgb_display.rgb import FourWire

spi = board.SPI()  # Use Pi hardware SPI
display_bus = FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin)

# Create display object
display = ST7789(display_bus, width=240, height=320, rotation=90)

# Clear display
display.fill(0)

# Draw test image
img = Image.new("RGB", (display.width, display.height))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
draw.text((10, 10), "Hello ST7789!", font=font, fill=(255, 255, 255))
draw.rectangle([50, 50, 150, 150], outline=(255, 0, 0), width=3)

display.image(img)
