import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
display = SSD1306_I2C(128, 64, i2c, addr=0x3c)

# Clear display
display.fill(0)
display.show()

# Create blank image for drawing
image = Image.new("1", (display.width, display.height))
draw = ImageDraw.Draw(image)

# Load a basic font
font = ImageFont.load_default()

# Draw text
draw.text((0, 0), "Hello, World!", font=font, fill=255)
draw.text((0, 20), "128x64 OLED", font=font, fill=255)

# Send to display
display.image(image)
display.show()
