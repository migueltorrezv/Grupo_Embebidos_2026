# Ejercicio 4 - Raspberry Pi 4
# Rampa PWM: 0% -> 100%, incremento 1% cada 0.5s
# Al llegar a 100% vuelve a 0% y repite

import RPi.GPIO as GPIO
from time import sleep

ENA = 12
IN1 = 20
IN2 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Direccion adelante
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

pwm = GPIO.PWM(ENA, 1000)  # 1 kHz
pwm.start(0)

try:
    while True:
        for dc in range(0, 101, 1): 
            pwm.ChangeDutyCycle(dc)
            print(f"Velocidad: {dc}%")
            sleep(0.5)
            
except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    pwm.stop()
    GPIO.cleanup()
