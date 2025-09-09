import spidev, RPi.GPIO as GPIO, time

# --- Pin setup (based on your wiring) ---
GPIO.setmode(GPIO.BCM)
DC = 22    # Data/Command
RST = 25   # Reset
CS = 24    # Chip Select
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)           # SPI bus 0, device CE0
spi.max_speed_hz = 40000000
spi.mode = 0

# --- Reset the display ---
GPIO.output(RST, 1); time.sleep(0.1)
GPIO.output(RST, 0); time.sleep(0.1)
GPIO.output(RST, 1); time.sleep(0.1)

# --- Initialization sequence ---
GPIO.output(DC, 0); spi.writebytes([0x01]); time.sleep(0.15)   # SWRESET
GPIO.output(DC, 0); spi.writebytes([0x11]); time.sleep(0.12)   # SLPOUT
GPIO.output(DC, 0); spi.writebytes([0x3A]); GPIO.output(DC,1); spi.writebytes([0x55])  # COLMOD: 16-bit color
GPIO.output(DC, 0); spi.writebytes([0x29]); time.sleep(0.1)    # DISPON

# --- Set column range (0-9 for 10 pixels) ---
GPIO.output(DC, 0); spi.writebytes([0x2A])                     # CASET
GPIO.output(DC, 1); spi.writebytes([0x00,0x00, 0x00,0x09])

# --- Set row range (0-9 for 10 pixels) ---
GPIO.output(DC, 0); spi.writebytes([0x2B])                     # RASET
GPIO.output(DC, 1); spi.writebytes([0x00,0x00, 0x00,0x09])

# --- Memory write ---
GPIO.output(DC, 0); spi.writebytes([0x2C])                     # RAMWR
GPIO.output(DC, 1)

# --- Fill the 10x10 area with green (RGB565 0x07E0) ---
hi, lo = 0x07, 0xE0
buf = [hi, lo] * 100    # 10x10 pixels
spi.writebytes(buf)

print("Done! You should see a 10x10 green square in the top-left corner.")
