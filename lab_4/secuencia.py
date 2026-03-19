import RPi.GPIO as GPIO
import time

LED1 = 18
LED2 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

def read_interval():
    try:
        with open("interval.txt", "r") as f:
            return float(f.read().strip())
    except:
        return 0.5

try:
    while True:
        interval = read_interval()
        GPIO.output(LED1, GPIO.HIGH)
        GPIO.output(LED2, GPIO.LOW)
        time.sleep(interval)
        GPIO.output(LED1, GPIO.LOW)
        GPIO.output(LED2, GPIO.HIGH)
        time.sleep(interval)
except KeyboardInterrupt:
    GPIO.cleanup()
