import spidev, RPi.GPIO as GPIO, time

# --- Pin setup ---
GPIO.setmode(GPIO.BCM)
DC = 22
RST = 25
CS = 24
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

# --- SPI setup ---
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 40000000
spi.mode = 0

# --- Reset display ---
GPIO.output(RST,1); time.sleep(0.1)
GPIO.output(RST,0); time.sleep(0.1)
GPIO.output(RST,1); time.sleep(0.1)

# --- Minimal init ---
GPIO.output(DC, 0); spi.writebytes([0x01]); time.sleep(0.15)  # SWRESET
GPIO.output(DC, 0); spi.writebytes([0x11]); time.sleep(0.12)  # SLPOUT
GPIO.output(DC, 0); spi.writebytes([0x3A]); GPIO.output(DC,1); spi.writebytes([0x55])  # 16-bit color
GPIO.output(DC, 0); spi.writebytes([0x29]); time.sleep(0.1)  # DISPON

# --- Test combinations ---
madctl_values = [0x00, 0x60, 0xC0]          # common rotation/RGB orders
row_offsets = [0x00, 0x60]                  # common 240x320 row offsets

for madctl in madctl_values:
    for row_offset in row_offsets:
        print(f"Testing MADCTL={hex(madctl)}, row_offset={hex(row_offset)}")
        
        # Set MADCTL
        GPIO.output(DC,0); spi.writebytes([0x36])
        GPIO.output(DC,1); spi.writebytes([madctl])
        
        # Column 0-0
        GPIO.output(DC,0); spi.writebytes([0x2A])
        GPIO.output(DC,1); spi.writebytes([0x00,0x00,0x00,0x00])
        
        # Row 0-0 with offset
        GPIO.output(DC,0); spi.writebytes([0x2B])
        GPIO.output(DC,1); spi.writebytes([0x00,row_offset,0x00,row_offset])
        
        # Memory write
        GPIO.output(DC,0); spi.writebytes([0x2C])
        GPIO.output(DC,1)
        
        # Single green pixel
        spi.writebytes([0x07,0xE0])
        
        time.sleep(1)  # wait a second so you can see if pixel appears
