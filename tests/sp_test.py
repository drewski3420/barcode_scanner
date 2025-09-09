import board, digitalio
from adafruit_rgb_display import st7789
from PIL import Image

spi = board.SPI()
dc = digitalio.DigitalInOut(board.D24)
cs = digitalio.DigitalInOut(board.CE0)
reset = digitalio.DigitalInOut(board.D25)

disp = st7789.ST7789(spi, cs=cs, dc=dc, rst=reset, baudrate=24000000,
                     width=240, height=320, x_offset=0, y_offset=0)

# Fill screen with GREEN
image = Image.new("RGB", (disp.width, disp.height), (0, 255, 0))
disp.image(image)
