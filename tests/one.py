import spidev
import RPi.GPIO as GPIO
import time

# --- Pin configuration (your mapping) ---
DC  = 15   # Data/Command
RST = 22   # Reset
CS  = 18   # Chip select
BL  = 17   # Backlight

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(BL, GPIO.OUT)

# Turn on backlight
GPIO.output(BL, 1)

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI bus 0, device 0
spi.max_speed_hz = 40000000  # 40 MHz
spi.mode = 0

# --- Helper to send commands/data ---
def cmd(val):
    GPIO.output(DC, 0)
    spi.writebytes([val])

def data(val):
    GPIO.output(DC, 1)
    if isinstance(val, list):
        spi.writebytes(val)
    else:
        spi.writebytes([val])

# --- Reset display ---
GPIO.output(RST, 0)
time.sleep(0.1)
GPIO.output(RST, 1)
time.sleep(0.1)

# --- Initialization sequence ---
cmd(0x01)  # SWRESET
time.sleep(0.15)

cmd(0x11)  # SLPOUT
time.sleep(0.12)

cmd(0x36)  # MADCTL
data(0x00)  # rotation = 0, RGB order false

cmd(0x3A)  # COLMOD
data(0x55)  # 16-bit color

cmd(0x21)  # INVON (invert colors as per LovyanGFX)

# Column address
cmd(0x2A)
data([0x00, 0x00, 0x00, 0xEF])  # 0 to 239

# Row address
cmd(0x2B)
data([0x00, 0x00, 0x01, 0x3F])  # 0 to 319

cmd(0x29)  # DISPON
time.sleep(0.1)

# --- Test: fill a single green pixel in top-left ---
cmd(0x2C)  # RAMWR
data([0x07, 0xE0])  # 16-bit green

print("Initialization complete. One green pixel should be visible.")
