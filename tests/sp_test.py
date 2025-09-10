import board
import displayio
import terminalio
from adafruit_display_text import label
from fourwire import FourWire
from adafruit_st7789 import ST7789

# Release any resources currently in use for the displays
displayio.release_displays()

# SPI setup
spi = board.SPI()
tft_cs = board.D5
tft_dc = board.D6

# Create the display bus
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.D9)

# Initialize the ST7789 display
# width=240, height=320, rotation=90 for clockwise 90°
display = ST7789(display_bus, width=240, height=320, rotation=90, bgr=True, invert=True)

# Make the display context
splash = displayio.Group()
display.root_group = splash

# Draw full-screen green background
color_bitmap = displayio.Bitmap(240, 320, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle (200x200)
inner_bitmap = displayio.Bitmap(200, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=20, y=60)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=2, x=50, y=160)
text_area = label.Label(terminalio.FONT, text="Hello World!", color=0xFFFF00)
text_group.append(text_area)
splash.append(text_group)

while True:
    pass
