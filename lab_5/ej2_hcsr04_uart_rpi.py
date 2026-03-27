# ============================================================
# Ejercicio 2 - Raspberry Pi 4
# HC-SR04 mide distancia y envia valor via UART a TIVA
#
# Conexiones HC-SR04:
#   VCC  -> 5V  (Pin 2)
#   GND  -> GND (Pin 6)
#   TRIG -> GPIO18 (Pin 12)
#   ECHO -> 330ohm -> GPIO24 (Pin 18) -> 470ohm -> GND
#           (divisor de tension: ECHO es 5V, GPIO tolera 3.3V)
#
# Conexion UART (USB):
#   TIVA USB microUSB -> Puerto USB de RPi (/dev/ttyACM0)
# ============================================================

import RPi.GPIO as GPIO
import serial
import time

TRIG = 18
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)

# UART hacia TIVA via USB
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()
time.sleep(0.5)  # esperar que TIVA inicialice

def medir_distancia():
    # Pulso TRIG de 10 microsegundos
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Esperar flanco de subida de ECHO (timeout 40ms)
    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 0:
        start = time.time()
        if time.time() > timeout:
            return -1.0

    # Esperar flanco de bajada de ECHO
    timeout = time.time() + 0.04
    while GPIO.input(ECHO) == 1:
        stop = time.time()
        if time.time() > timeout:
            return -1.0

    # distancia [cm] = (tiempo [s] * 34300 cm/s) / 2
    return round((stop - start) * 34300 / 2, 2)

try:
    while True:
        dist = medir_distancia()

        if dist < 0:
            print("Error de lectura, reintentando...")
        else:
            print(f"Distancia: {dist} cm")
            # Enviar a TIVA como string con newline
            ser.write(f"{dist}\n".encode('utf-8'))

        time.sleep(0.2)  # 5 mediciones por segundo

except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    GPIO.cleanup()
    ser.close()
