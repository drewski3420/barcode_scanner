import time
import board
import digitalio
import adafruit_st7789

# Set up the SPI bus and pins
spi = board.SPI()
dc = digitalio.DigitalInOut(board.D24)
reset = digitalio.DigitalInOut(board.D25)
#cs = digitalio.DigitalInOut(board.D8)

# Initialize the display
display = adafruit_st7789.ST7789(
    spi,
    width=240,
    height=320,
    reset=reset,
    dc=dc,
    cs_pin=board.CE0,   # <- use cs_pin instead of cs
    rotation=90
)

# Fill the screen with a color
display.fill(0x00FF00)  # Green

# Wait for a while
time.sleep(5)

# Fill the screen with another color
display.fill(0x0000FF)  # Blue

# Wait for a while
time.sleep(5)

# Fill the screen with another color
display.fill(0xFF0000)  # Red

# Wait for a while
time.sleep(5)

# Clear the display
display.fill(0x000000)  # Black
