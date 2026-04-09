import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pines configurados según tu setup
LED1, LED2 = 18, 23
B1 = 8

GPIO.setup([LED1, LED2], GPIO.OUT)
GPIO.setup(B1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Empezamos en estado 0 (Apagado)
estado = 0

try:
    print("Sistema iniciado en Estado 0 (Apagado)")
    
    while True:
        # Detección del botón (B1)
        if GPIO.input(B1) == GPIO.LOW:
            estado = estado + 1
            
            # Si llega al estado 4, vuelve al estado 0
            if estado > 3:
                estado = 0
            
            print(f"Cambiando a Estado: {estado}")
            
            # Retardo para evitar rebote mecánico
            time.sleep(0.05)
            while GPIO.input(B1) == GPIO.LOW:
                time.sleep(0.01)

        # EJECUCIÓN DE LOS ESTADOS
        
        if estado == 1:
            # Estado 1: Parpadean uno sí y otro no (Alternado)
            GPIO.output(LED1, GPIO.HIGH)
            GPIO.output(LED2, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(LED1, GPIO.LOW)
            GPIO.output(LED2, GPIO.HIGH)
            time.sleep(0.5)

        elif estado == 2:
            # Estado 2: Parpadean ambos al mismo tiempo (Simultáneo)
            GPIO.output(LED1, GPIO.HIGH)
            GPIO.output(LED2, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(LED1, GPIO.LOW)
            GPIO.output(LED2, GPIO.LOW)
            time.sleep(0.5)

        elif estado == 3:
            # Estado 3: Ambos encendidos fijo
            GPIO.output(LED1, GPIO.HIGH)
            GPIO.output(LED2, GPIO.HIGH)

        elif estado == 0:
            # Estado 0: Ambos apagados (Reinicio)
            GPIO.output(LED1, GPIO.LOW)
            GPIO.output(LED2, GPIO.LOW)

        time.sleep(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
