import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Definicion de pines
LED1, LED2, LED3, LED4 = 18, 23, 24, 25
B1, B2 = 8, 7

GPIO.setup([LED1, LED2, LED3, LED4], GPIO.OUT)
GPIO.setup([B1, B2], GPIO.IN, pull_up_down=GPIO.PUD_UP)

contador = 0

def actualizar_leds(n):
    # Estado: Actualizando LEDs segun el valor del contador
    GPIO.output(LED1, n & 0x01)
    GPIO.output(LED2, (n >> 1) & 0x01)
    GPIO.output(LED3, (n >> 2) & 0x01)
    GPIO.output(LED4, (n >> 3) & 0x01)

try:
    actualizar_leds(0)
    print("Contador listo. B1: Sube, B2: Baja")

    while True:
        # Estado: Monitoreo de botones
        
        # Boton 1: Incrementar
        if GPIO.input(B1) == GPIO.LOW:
            contador = contador + 1
            if contador > 15:
                contador = 0
            
            print(f"Estado actual: {contador}")
            actualizar_leds(contador)
            
            time.sleep(0.05) # Retardo mecanico minimo
            while GPIO.input(B1) == GPIO.LOW:
                time.sleep(0.01)

        # Boton 2: Decrementar (con limite en 0)
        if GPIO.input(B2) == GPIO.LOW:
            if contador > 0:
                contador = contador - 1
                # Estado: Bajando valor del contador
            else:
                # Estado: Intento de bajar mas de 0 (bloqueado)
                print("Limite alcanzado: No puede bajar de 0")
            
            print(f"Estado actual: {contador}")
            actualizar_leds(contador)
            
            time.sleep(0.05) # Retardo mecanico minimo
            while GPIO.input(B2) == GPIO.LOW:
                time.sleep(0.01)

        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
