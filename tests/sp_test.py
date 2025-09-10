import board
import digitalio
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_st7789

# SPI setup
spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)
cs_pin = digitalio.DigitalInOut(board.CE0)  # Chip select
dc_pin = digitalio.DigitalInOut(board.D24)  # Data/Command
reset_pin = digitalio.DigitalInOut(board.D25)  # Reset

# Initialize display
display = adafruit_st7789.ST7789(
    spi=spi,          # Note the keyword
    cs=cs_pin,        # Correct keyword
    dc=dc_pin,        # Correct keyword
    rst=reset_pin,    # Correct keyword
    width=240,
    height=320,
    rotation=90,
    baudrate=24000000
)

# Clear the display
display.fill(0)

# Create blank image for drawing
img = Image.new("RGB", (display.width, display.height))
draw = ImageDraw.Draw(img)

# Load default font
font = ImageFont.load_default()

# Draw some text
draw.text((10, 10), "Hello ST7789!", font=font, fill=(255, 255, 255))
draw.rectangle([50, 50, 150, 150], outline=(255, 0, 0), width=3)

# Display the image
display.image(img)
