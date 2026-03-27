# ============================================================
# Ejercicio 3 - Raspberry Pi 4
# PWM Motor DC a duty cycles fijos: 75%, 25%, 45%, 50%
#
# Conexiones L298N -> RPi:
#   ENA  -> GPIO12 (Pin 32) [PWM hardware]
#   IN1  -> GPIO20 (Pin 38)
#   IN2  -> GPIO21 (Pin 40)
#   VCC motor -> Bateria 9V (+)
#   GND  -> GND RPi (Pin 34) + GND Bateria
#   OUT1 -> Motor terminal A
#   OUT2 -> Motor terminal B
# ============================================================

import RPi.GPIO as GPIO
from time import sleep

ENA = 12  # PWM hardware
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

duty_cycles = [75, 25, 45, 50]

try:
    for dc in duty_cycles:
        print(f"Duty cycle: {dc}%")
        pwm.ChangeDutyCycle(dc)
        sleep(3)

    print("Ciclo completo, deteniendo motor.")
    pwm.ChangeDutyCycle(0)

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
