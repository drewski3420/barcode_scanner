#!/usr/bin/env python3
from time import sleep
from PIL import Image, ImageDraw, ImageFont

from RPi import GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from luma.core.framebuffer import diff_to_previous

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

interface = spi(
    port=0,
    device=0,
    gpio=GPIO,
    bus_speed_hz=8000000,
    transfer_size=4096,
    gpio_DC=25,
    gpio_RST=24
)

fb = diff_to_previous(num_segments=4, debug=True)
backlight_params = dict(
    gpio=interface._gpio,
    gpio_LIGHT=18,          # optional backlight pin
    active_low=True         # matches demo.py backlight_active='low'
)

device = st7789(
    serial_interface=interface,
    width=320,
    height=240,
    rotate=2,
    mode="RGB",
    framebuffer=fb,
    bgr=False,
    inverse=False,
    h_offset=0,
    v_offset=0,
    num_segments=4,
    block_orientation=0,
    **backlight_params
)
