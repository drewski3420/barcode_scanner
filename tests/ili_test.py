import board, digitalio
from adafruit_rgb_display import ili9341
from PIL import Image

spi = board.SPI()
dc = digitalio.DigitalInOut(board.D24)
cs = digitalio.DigitalInOut(board.CE0)
reset = digitalio.DigitalInOut(board.D25)

disp = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=reset, baudrate=24000000)

# Fill screen with RED
image = Image.new("RGB", (disp.width, disp.height), (255, 0, 0))
disp.image(image)
