import RPi.GPIO as GPIO
import time

LED_PIN = 18
BTN_START = 17
BTN_STOP = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BTN_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_STOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

led_on = False

try:
    while True:
        if GPIO.input(BTN_START) == GPIO.LOW:
            led_on = True
        if GPIO.input(BTN_STOP) == GPIO.LOW:
            led_on = False
        GPIO.output(LED_PIN, GPIO.HIGH if led_on else GPIO.LOW)
        time.sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup()
