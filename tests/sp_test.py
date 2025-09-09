import spidev
import RPi.GPIO as GPIO
import time

# Pin numbers (BCM)
DC_PIN = 24    # Data/Command
RST_PIN = 25   # Reset
CS = 0         # SPI CE0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RST_PIN, GPIO.OUT)

# Reset sequence
GPIO.output(RST_PIN, 0)
time.sleep(0.1)
GPIO.output(RST_PIN, 1)
time.sleep(0.1)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, CS)
spi.max_speed_hz = 4000000
spi.mode = 0

def write_cmd(cmd):
    GPIO.output(DC_PIN, 0)  # command
    spi.xfer2([cmd])

def write_data(data):
    GPIO.output(DC_PIN, 1)  # data
    if isinstance(data, int):
        spi.xfer2([data])
    else:
        spi.xfer2(data)

# --- ST7789 minimal init sequence ---
write_cmd(0x01)  # Software reset
time.sleep(0.15)

write_cmd(0x11)  # Sleep out
time.sleep(0.15)

write_cmd(0x36)  # Memory Access Control
write_data(0x00) # RGB, no rotation

write_cmd(0x3A)  # Interface pixel format
write_data(0x05) # 16-bit/pixel

write_cmd(0x29)  # Display ON
time.sleep(0.05)

# --- Fill screen green ---
def set_window(x0, y0, x1, y1):
    write_cmd(0x2A)  # Column addr
    write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
    write_cmd(0x2B)  # Row addr
    write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
    write_cmd(0x2C)  # Write RAM

width, height = 240, 320
set_window(0, 0, width - 1, height - 1)

# Send solid green (RGB565: 0x07E0)
color = [0x07, 0xE0] * width
GPIO.output(DC_PIN, 1)
for _ in range(height):
    spi.xfer2(color)

print("Filled screen green")

spi.close()
GPIO.cleanup()
