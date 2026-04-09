import RPi.GPIO as GPIO
import time

# Configuración de pines
LEDS = [18, 23, 24, 25]
B_SELECCION = 8
B_TIEMPO = 7

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEDS, GPIO.OUT)
GPIO.setup([B_SELECCION, B_TIEMPO], GPIO.IN, pull_up_down=GPIO.PUD_UP)

led_actual = 0 
tiempo_encendido = 1

def resetear_leds():
    GPIO.output(LEDS, GPIO.LOW)

def mostrar_configuracion(led_idx, t):
    # Ahora imprime el numero de LED (0 a 3)
    print(f"LED seleccionado: LED {led_idx} | Tiempo: {t} seg")

def encender_seleccionado():
    resetear_leds()
    GPIO.output(LEDS[led_actual], GPIO.HIGH)
    time.sleep(tiempo_encendido)
    resetear_leds()

try:
    print(" Boton1: Seleccion LED,          Boton2: +1 Segundo")
    mostrar_configuracion(led_actual, tiempo_encendido)

    while True:
        if GPIO.input(B_SELECCION) == GPIO.LOW:
            led_actual = (led_actual + 1) % 4
            tiempo_encendido = 1
            
            mostrar_configuracion(led_actual, tiempo_encendido)
            encender_seleccionado()
            
            time.sleep(0.05)
            while GPIO.input(B_SELECCION) == GPIO.LOW:
                time.sleep(0.01)

        if GPIO.input(B_TIEMPO) == GPIO.LOW:
            tiempo_encendido += 1
            
            mostrar_configuracion(led_actual, tiempo_encendido)
            encender_seleccionado()
            
            time.sleep(0.05)
            while GPIO.input(B_TIEMPO) == GPIO.LOW:
                time.sleep(0.01)

        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
