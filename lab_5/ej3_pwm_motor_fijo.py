# Ejercicio 3 - Raspberry Pi 4
# PWM Motor DC a duty cycles fijos: 75%, 25%, 45%, 50%


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


GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

pwm = GPIO.PWM(ENA, 1000)  # 1 kHz
pwm.start(0)

duty_cycles = [75, 25, 45, 50]

try:
    for dc in duty_cycles:
        print(f"Duty cycle: {dc}%")
        pwm.ChangeDutyCycle(dc)
<<<<<<< HEAD
        sleep(4)  # 4 segundos por velocidad
=======
        sleep(3)
>>>>>>> 654c3870c0ea79f235d840f6bbaedcfec2314b5c

    print("Ciclo completo, deteniendo motor.")
    pwm.ChangeDutyCycle(0)

except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
