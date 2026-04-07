# ============================================================
# Ejercicio 2 - Raspberry Pi 4
# HC-SR04 mide distancia y envia valor via UART a TIVA
#
# Conexiones HC-SR04:
#   VCC  -> Pin 2  (5V)
#   GND  -> Pin 6  (GND)
#   TRIG -> Pin 12 (GPIO18)
#   ECHO -> 330ohm -> Pin 18 (GPIO24) -> 470ohm -> GND
#
# Conexion UART:
#   TIVA micro-USB -> puerto USB RPi -> /dev/ttyACM0
# ============================================================

import RPi.GPIO as GPIO
import serial
import time

TRIG = 18
ECHO = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
time.sleep(0.5)  # estabilizar sensor al inicio

# UART hacia TIVA
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
ser.reset_input_buffer()

def medir_distancia():
    # Pulso TRIG 10us
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Esperar subida ECHO
    while GPIO.input(ECHO) == 0:
        inicio_pulso = time.time()

    # Esperar bajada ECHO
    while GPIO.input(ECHO) == 1:
        fin_pulso = time.time()

    distancia = ((fin_pulso - inicio_pulso) * 34300) / 2
    return round(distancia, 2)

try:
    print("Iniciando... Ctrl+C para detener.")
    while True:
        dist = medir_distancia()
        print(f"Distancia: {dist} cm")
        ser.write(f"{dist}\n".encode('utf-8'))
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    GPIO.cleanup()
    ser.close()