# Ejercicio 2 - Raspberry Pi 4
# HC-SR04 mide distancia y envia valor via UART a TIVA

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
time.sleep(0.5)  


ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser.reset_input_buffer()

def medir_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        inicio_pulso = time.time()

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
