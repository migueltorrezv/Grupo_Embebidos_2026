import RPi.GPIO as GPIO
import time
import random   

GPIO.setmode(GPIO.BCM)

LED1 = 18
LED2 = 23

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

try:
    while True:

        # Generar número aleatorio
        numero = random.randint(0,50)

        print("Numero generado:", numero)

        # Apagar ambos LEDs primero
        GPIO.output(LED1, GPIO.LOW)
        GPIO.output(LED2, GPIO.LOW)

        # Condiciones
        if numero < 12:
            GPIO.output(LED1, GPIO.HIGH)
            print("Se enciende led1 CALENTADOR")

        elif numero > 20:
            GPIO.output(LED2, GPIO.HIGH)
            print("Se enciende led2 VENTILADOR")

        else:
            print("Numero entre 12 y 20, no se enciende ningún LED")

        time.sleep(4)

except KeyboardInterrupt:
    print("Programa detenido")

finally:
    GPIO.cleanup()
