import spidev
import RPi.GPIO as GPIO
import time

# --- Pins (BCM) ---
DC = 24
RST = 25
BL = 18  # optional if you want to toggle backlight via GPIO

# --- Setup GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(BL, GPIO.OUT)
GPIO.output(BL, 1)  # backlight on

# --- Reset the display ---
GPIO.output(RST, 0)
time.sleep(0.1)
GPIO.output(RST, 1)
time.sleep(0.1)

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)       # SPI0, CE0
spi.max_speed_hz = 4000000
spi.mode = 3         # try 3 if 0 doesn’t work

# --- Helper functions ---
def write_cmd(cmd):
    GPIO.output(DC, 0)
    spi.xfer2([cmd])

def write_data(data):
    GPIO.output(DC, 1)
    if isinstance(data, int):
        spi.xfer2([data])
    else:
        spi.xfer2(data)

# --- Minimal ST7789 init sequence ---
write_cmd(0x01)  # Software reset
time.sleep(0.15)
write_cmd(0x11)  # Sleep out
time.sleep(0.15)
write_cmd(0x36)  # Memory Access Control
write_data(0x00)
write_cmd(0x3A)  # Pixel format
write_data(0x05)  # 16-bit/pixel
write_cmd(0x29)  # Display ON
time.sleep(0.05)

# --- Fill screen with green ---
def set_window(x0, y0, x1, y1):
    write_cmd(0x2A)  # Column addr
    write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
    write_cmd(0x2B)  # Row addr
    write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
    write_cmd(0x2C)  # Write RAM

width, height = 240, 320
set_window(0, 0, width-1, height-1)

# Fill screen with solid green (RGB565: 0x07E0)
color = [0x07, 0xE0] * width
GPIO.output(DC, 1)
for _ in range(height):
    spi.xfer2(color)

print("Screen should be green now")

spi.close()
GPIO.cleanup()
