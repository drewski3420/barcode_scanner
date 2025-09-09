import RPi.GPIO as GPIO
import time

BL_PIN = 18  # GPIO18, header pin 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(BL_PIN, GPIO.OUT)

print("Backlight ON for 3 seconds...")
GPIO.output(BL_PIN, GPIO.HIGH)
time.sleep(3)

print("Backlight OFF for 3 seconds...")
GPIO.output(BL_PIN, GPIO.LOW)
time.sleep(3)

GPIO.cleanup()
