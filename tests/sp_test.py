import time
import board
import digitalio
import adafruit_st7789

# SPI pins
spi = board.SPI()
dc = digitalio.DigitalInOut(board.D24)

# CS pin (CE0)
cs = board.CE0

# Reset pin manually
reset = digitalio.DigitalInOut(board.D25)
reset.direction = digitalio.Direction.OUTPUT
# Toggle reset
reset.value = False
time.sleep(0.1)
reset.value = True
time.sleep(0.1)

# Initialize display
display = adafruit_st7789.ST7789(
    spi,
    dc=dc,
    cs_pin=cs,
    width=240,
    height=320,
    rotation=90
)

# Fill screen with colors
display.fill(0x00FF00)  # Green
time.sleep(2)
display.fill(0x0000FF)  # Blue
time.sleep(2)
display.fill(0xFF0000)  # Red
time.sleep(2)
display.fill(0x000000)  # Black
