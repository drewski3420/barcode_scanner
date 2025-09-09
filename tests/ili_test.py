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

# --- ILI9341 minimal init sequence ---
write_cmd(0x01)  # Software reset
time.sleep(0.1)

write_cmd(0x28)  # Display OFF

write_cmd(0x3A)  # Pixel format
write_data(0x55)  # 16-bit/pixel

write_cmd(0x36)  # Memory Access Control
write_data(0x48)  # MX, BGR

write_cmd(0x11)  # Sleep out
time.sleep(0.12)

write_cmd(0x2_
