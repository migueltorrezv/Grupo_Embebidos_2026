# ============================================================
# Ejercicio 3 - Raspberry Pi 4
# PWM Motor DC a duty cycles fijos: 75%, 45%, 50%, 25%
#
# Conexiones L298N -> RPi:
#   ENA  -> GPIO12 (PWM hardware)
#   IN1  -> GPIO20
#   IN2  -> GPIO21
#   VCC motor -> Bateria 9V (+)
#   GND  -> GND RPi + GND Bateria
#   OUT1 -> Motor terminal A
#   OUT2 -> Motor terminal B
# ============================================================

import RPi.GPIO as GPIO
from time import sleep

ENA = 12  # PWM hardware (GPIO12 = PWM0)
IN1 = 20  # control direccion
IN2 = 21  # control direccion

GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# Direccion: adelante
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

# PWM a 1 kHz (adecuado para motor DC)
pwm = GPIO.PWM(ENA, 1000)
pwm.start(0)

duty_cycles = [75, 25, 45, 50]  # orden del enunciado

try:
    for dc in duty_cycles:
        print(f"Duty cycle: {dc}%")
        pwm.ChangeDutyCycle(dc)
        sleep(3)  # 3 segundos por velocidad

    print("Ciclo completo, deteniendo motor.")
    pwm.ChangeDutyCycle(0)

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
